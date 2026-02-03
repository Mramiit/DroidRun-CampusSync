from droidrun import DroidAgent
import inspect

print("--- DroidAgent Constructor Arguments ---")
signature = inspect.signature(DroidAgent.__init__)
for name, param in signature.parameters.items():
    print(f"{name}: {param.default}")