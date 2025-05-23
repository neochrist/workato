from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass(frozen=True)
class Schema:
    """Represents input or output schema for recipe components."""
    fields: Dict[str, str]
    
    def __str__(self) -> str:
        field_strs = [f"{name}: {type_}" for name, type_ in self.fields.items()]
        return "{" + ", ".join(field_strs) + "}"


class RecipeComponent(ABC):
    """Abstract base class for all recipe components."""
    
    def __init__(self, name: str, input_schema: Schema, output_schema: Schema) -> None:
        self._name = name
        self._input_schema = input_schema
        self._output_schema = output_schema
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def input_schema(self) -> Schema:
        return self._input_schema
    
    @property
    def output_schema(self) -> Schema:
        return self._output_schema
    
    @abstractmethod
    def get_children(self) -> List['RecipeComponent']:
        """Return list of child components."""
        pass


class Trigger(RecipeComponent):
    """Represents a recipe trigger (e.g., cron job, external event)."""
    
    def __init__(self, name: str, input_schema: Schema, output_schema: Schema, 
                 trigger_type: str) -> None:
        super().__init__(name, input_schema, output_schema)
        self._trigger_type = trigger_type
    
    @property
    def trigger_type(self) -> str:
        return self._trigger_type
    
    def get_children(self) -> List[RecipeComponent]:
        return []


class Action(RecipeComponent):
    """Represents a recipe action that can contain nested actions."""
    
    def __init__(self, name: str, input_schema: Schema, output_schema: Schema,
                 action_type: str, nested_actions: Optional[List['Action']] = None) -> None:
        super().__init__(name, input_schema, output_schema)
        self._action_type = action_type
        self._nested_actions = nested_actions or []
    
    @property
    def action_type(self) -> str:
        return self._action_type
    
    @property
    def nested_actions(self) -> List['Action']:
        return self._nested_actions.copy()
    
    def add_nested_action(self, action: 'Action') -> None:
        """Add a nested action to this action."""
        self._nested_actions.append(action)
    
    def get_children(self) -> List[RecipeComponent]:
        return list(self._nested_actions)


class Recipe:
    """Represents a complete Workato recipe with trigger and actions."""
    
    def __init__(self, name: str, trigger: Trigger, actions: Optional[List[Action]] = None) -> None:
        self._name = name
        self._trigger = trigger
        self._actions = actions or []
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def trigger(self) -> Trigger:
        return self._trigger
    
    @property
    def actions(self) -> List[Action]:
        return self._actions.copy()
    
    def add_action(self, action: Action) -> None:
        """Add an action to the recipe."""
        self._actions.append(action)


def traverse_recipe(recipe: Recipe) -> None:
    """Traverse and print all recipe components with their schemas and indices."""
    
    def _traverse_component(component: RecipeComponent, global_counter: List[int], 
                          nested_path: List[int]) -> None:
        global_counter[0] += 1
        current_global = global_counter[0]
        
        # Build nested index string
        nested_index = ".".join(map(str, nested_path))
        
        component_type = "T" if isinstance(component, Trigger) else component.name
        
        print(f"({current_global}) {nested_index}: {component_type} "
              f"(input_schema={component.input_schema}, output_schema={component.output_schema})")
        
        # Traverse children
        children = component.get_children()
        for i, child in enumerate(children, 1):
            child_path = nested_path + [i]
            _traverse_component(child, global_counter, child_path)
    
    print(f"Recipe: {recipe.name}")
    
    # Start with trigger (index 1)
    global_counter = [0]
    _traverse_component(recipe.trigger, global_counter, [1])
    
    # Traverse top-level actions (indices 2, 3, 4, ...)
    for i, action in enumerate(recipe.actions, 2):
        _traverse_component(action, global_counter, [i])


def create_example_recipe() -> Recipe:
    """Create an example recipe matching the specified structure."""
    
    # Create schemas
    trigger_input = Schema({"schedule": "string"})
    trigger_output = Schema({"timestamp": "datetime", "event_id": "string"})
    
    action_input = Schema({"data": "object"})
    action_output = Schema({"result": "string", "status": "boolean"})
    
    nested_input = Schema({"value": "number"})
    nested_output = Schema({"processed_value": "number"})
    
    # Create trigger
    trigger = Trigger("T", trigger_input, trigger_output, "cron")
    
    # Create actions
    a1 = Action("A1", action_input, action_output, "data_processing")
    
    # Create nested actions for A2
    a2_1 = Action("A2.1", nested_input, nested_output, "calculation")
    
    a2_2_1 = Action("A2.2.1", nested_input, nested_output, "validation")
    a2_2 = Action("A2.2", nested_input, nested_output, "transformation")
    a2_2.add_nested_action(a2_2_1)
    
    a2 = Action("A2", action_input, action_output, "complex_processing")
    a2.add_nested_action(a2_1)
    a2.add_nested_action(a2_2)
    
    a3 = Action("A3", action_input, action_output, "final_processing")
    
    # Create recipe
    recipe = Recipe("Example Recipe", trigger)
    recipe.add_action(a1)
    recipe.add_action(a2)
    recipe.add_action(a3)
    
    return recipe


if __name__ == "__main__":
    # Create and traverse the example recipe
    example_recipe = create_example_recipe()
    traverse_recipe(example_recipe) 