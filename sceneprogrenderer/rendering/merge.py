import bpy
import os

def merge_glb_files():
    """
    Combines multiple .glb files into a single .glb file.

    Parameters:
        input_directory (str): Directory containing the .glb files to merge.
        output_file (str): Path to save the combined .glb file.
    """
    with open('merge_params.txt', 'r') as f:
        input_directory = f.readline().strip()
        output_file = f.readline().strip()
        
    # Clear the current scene
    bpy.ops.wm.read_factory_settings(use_empty=True)

    # Create a new collection for imported objects
    merged_collection = bpy.data.collections.new("MergedCollection")
    bpy.context.scene.collection.children.link(merged_collection)

    # Import all .glb files from the input directory
    for file_name in os.listdir(input_directory):
        if file_name.endswith(".glb"):
            if 'ceiling' in file_name:
                continue
            if 'door' in file_name:
                continue
            file_path = os.path.join(input_directory, file_name)
            bpy.ops.import_scene.gltf(filepath=file_path)

            # Move imported objects to the merged collection
            imported_objects = [obj for obj in bpy.context.scene.objects if obj.select_get()]
            for obj in imported_objects:
                bpy.context.scene.collection.objects.unlink(obj)
                merged_collection.objects.link(obj)

            print(f"Imported {file_name}")

    # Export the combined .glb file
    bpy.ops.export_scene.gltf(filepath=output_file, export_format='GLB')
    print(f"Combined .glb file saved to {output_file}")

if __name__ == "__main__":

    merge_glb_files()
    