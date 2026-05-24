from abc import ABC, abstractmethod

class BaseTool(ABC):
    @property
    @abstractmethod
    def name(self) -> str: pass

    @property
    @abstractmethod
    def description(self) -> str: pass

    @property
    @abstractmethod
    def parameters(self) -> dict: pass

    @abstractmethod
    def execute(self, **kwargs) -> str:
        pass


class UnityDynamicTool(BaseTool):
    """A proxy tool that represents a method existing inside Unity."""
    def __init__(self, name, description, parameters):
        self._name = name
        self._description = description
        self._parameters = parameters

    @property
    def name(self) -> str: return self._name

    @property
    def description(self) -> str: return self._description

    @property
    def parameters(self) -> dict: return self._parameters

    def execute(self, **kwargs) -> str:
        # We return a special prefix so the C# side knows it must 
        # actually run the logic in the VR engine.
        return f"[UNITY_EXECUTE] {self.name} with {kwargs}"




class Load3DObject(BaseTool):
    name = "load_3d_object"
    description = "Load a 3D object into the scene."
    parameters = {"objpath": "string", "mtlpath": "string"}

    def execute(self, objpath: str, mtlpath: str = "", **kwargs) -> str:
        # In a real VR setup, this might send a signal to Unity
        return f"Successfully loaded {objpath}"

    
class GenerateBall(BaseTool):
    name = "generate_ball"
    description = "Generate a ball file ready for loading"
    parameters = {"path_to_generate_to": "string"}

    def execute(self, path_to_generate_to: str, **kwargs) -> str:
        # In a real VR setup, this might send a signal to Unity
        return f"Successfully loaded {path_to_generate_to}"