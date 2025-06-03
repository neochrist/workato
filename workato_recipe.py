from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Type
from dataclasses import dataclass, field

Schema = Dict[str, Type[Any]]


@dataclass
class RecipeComponent(ABC):
    """Abstract base class for all recipe components."""
    name: str
    input_schema: Schema
    output_schema: Schema
    
    @abstractmethod
    def get_children(self) -> List['RecipeComponent']:
        """Return list of child components."""
        pass


@dataclass
class Trigger(RecipeComponent):
    """Represents a recipe trigger (e.g., cron job, external event)."""
    trigger_type: str
    
    def get_children(self) -> List[RecipeComponent]:
        return []


@dataclass
class Action(RecipeComponent):
    """Represents a recipe action that can contain nested actions."""
    action_type: str
    nested_actions: List['Action'] = field(default_factory=list)
    
    def add_nested_action(self, action: 'Action') -> None:
        """Add a nested action to this action."""
        self.nested_actions.append(action)
    
    def get_children(self) -> List[RecipeComponent]:
        return list(self.nested_actions)


@dataclass
class Recipe:
    """Represents a complete Workato recipe with trigger and actions."""
    name: str
    trigger: Trigger
    actions: List[Action] = field(default_factory=list)
    
    def add_action(self, action: Action) -> None:
        """Add an action to the recipe."""
        self.actions.append(action)
    
    def traverse(self) -> None:
        """Traverse and print all recipe components with their schemas and indices."""
        
        def _traverse_component(
            component: RecipeComponent,
            global_counter: List[int],
            nested_path: List[int]
        ) -> None:
            global_counter[0] += 1
            current_global = global_counter[0]

            nested_index = ".".join(map(str, nested_path))
            
            component_type = "T" if component is self.trigger else component.name
            
            input_schema_str = _format_schema(component.input_schema)
            output_schema_str = _format_schema(component.output_schema)
            
            print(f"({current_global}) {nested_index}: {component_type} "
                  f"(input_schema={input_schema_str}, output_schema={output_schema_str})")

            children = component.get_children()
            for i, child in enumerate(children, 1):
                child_path = nested_path + [i]
                _traverse_component(child, global_counter, child_path)
        
        def _format_schema(schema: Schema) -> str:
            """Format schema dictionary for display."""
            field_strs = [f"{name}: {type_.__name__}" for name, type_ in schema.items()]
            return "{" + ", ".join(field_strs) + "}"
        
        print(f"Recipe: {self.name}")
        
        global_counter = [0]
        _traverse_component(self.trigger, global_counter, [1])

        for i, action in enumerate(self.actions, 2):
            _traverse_component(action, global_counter, [i])


def create_example_recipe() -> Recipe:
    """Create an example recipe matching the specified structure."""

    trigger_input = {"schedule": str}
    trigger_output = {"timestamp": str, "event_id": str}
    
    action_input = {"data": dict}
    action_output = {"result": str, "status": bool}
    
    nested_input = {"value": int}
    nested_output = {"processed_value": int}
    
    trigger = Trigger(
        name="T",
        input_schema=trigger_input,
        output_schema=trigger_output,
        trigger_type="cron"
    )

    a1 = Action(
        name="A1",
        input_schema=action_input,
        output_schema=action_output,
        action_type="data_processing"
    )
    
    a2_1 = Action(
        name="A2.1",
        input_schema=nested_input,
        output_schema=nested_output,
        action_type="calculation"
    )
    
    a2_2_1 = Action(
        name="A2.2.1",
        input_schema=nested_input,
        output_schema=nested_output,
        action_type="validation"
    )
    
    a2_2 = Action(
        name="A2.2",
        input_schema=nested_input,
        output_schema=nested_output,
        action_type="transformation"
    )
    a2_2.add_nested_action(a2_2_1)
    
    a2 = Action(
        name="A2",
        input_schema=action_input,
        output_schema=action_output,
        action_type="complex_processing"
    )
    a2.add_nested_action(a2_1)
    a2.add_nested_action(a2_2)
    
    a3 = Action(
        name="A3",
        input_schema=action_input,
        output_schema=action_output,
        action_type="final_processing"
    )
    
    recipe = Recipe("Example Recipe", trigger)
    recipe.add_action(a1)
    recipe.add_action(a2)
    recipe.add_action(a3)
    
    return recipe


if __name__ == "__main__":
    example_recipe = create_example_recipe()
    example_recipe.traverse() 