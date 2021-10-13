import glob
import inspect
import os
import importlib

def import_all_probes(probes_dir='./probe_system/probes', probes_package='probe_system.probes', base_class=None, create_instance=True, filter_abstract=True):

    plugin_file_paths = glob.glob(os.path.join(probes_dir, "*.py"))
    for plugin_file_path in plugin_file_paths:
        plugin_file_name = os.path.basename(plugin_file_path)
        
        module_name = os.path.splitext(plugin_file_name)[0]

        if module_name.startswith("__"):
            continue

        module = importlib.import_module("." + module_name, package=probes_package)

        for item in dir(module):
            value = getattr(module, item)
            if not value:
                continue
            
            if inspect.isabstract(value):
                continue

            if not inspect.isclass(value):
                continue

            if filter_abstract and inspect.isabstract(value):
                continue

            if base_class is not None and type(value) != type(base_class):
                continue
            
            yield value() if create_instance else value