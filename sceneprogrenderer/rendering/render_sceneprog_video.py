def render(glb_directory, output_directory, downsample=1):
    with open('sceneprog_params.txt', 'w') as f:
        f.write(glb_directory + '\n')
        f.write(output_directory + '\n')
        f.write(str(downsample) + '\n')

    import subprocess

    blender_executable_path = '/Applications/Blender.app/Contents/MacOS/Blender'
    script_path = '/Users/kunalgupta/Documents/rendering/worker_sceneprog_render_video.py'

    command = [
        blender_executable_path,
        '--background',
        '--python', script_path,
    ]

    try:
        print(f"Executing Blender script with: {' '.join(command)}")
        process = subprocess.run(command, timeout=300, text=True, capture_output=True)
        print("Blender Output:\n", process.stdout)
        print("Blender Errors:\n", process.stderr)
    except subprocess.TimeoutExpired:
        print("Blender process exceeded the time limit and was terminated.")
    except subprocess.CalledProcessError as e:
        print(f"Blender process failed with error:\n{e.stderr}")
    except Exception as e:
        print(f"Unexpected error occurred: {str(e)}")
        
def merge(input_directory, output_file):
    with open('merge_params.txt', 'w') as f:
        f.write(input_directory + '\n')
        f.write(output_file + '\n')

    import subprocess

    blender_executable_path = '/Applications/Blender.app/Contents/MacOS/Blender'
    script_path = '/Users/kunalgupta/Documents/rendering/merge.py'

    command = [
        blender_executable_path,
        '--background',
        '--python', script_path,
    ]

    try:
        print(f"Executing Blender script with: {' '.join(command)}")
        process = subprocess.run(command, timeout=300, text=True, capture_output=True)
        print("Blender Output:\n", process.stdout)
        print("Blender Errors:\n", process.stderr)
    except subprocess.TimeoutExpired:
        print("Blender process exceeded the time limit and was terminated.")
    except subprocess.CalledProcessError as e:
        print(f"Blender process failed with error:\n{e.stderr}")
    except Exception as e:
        print(f"Unexpected error occurred: {str(e)}")
        
# Example Usage

import os
for file in os.listdir('/Users/kunalgupta/Documents/results'):
    try:
        if '.DS_Store' in file:
            continue
        
        if file not in ['buffet_0','grocery_0','grocery_1']:
            continue
        
        os.makedirs(f"/Users/kunalgupta/Documents/single_sceneprog/{file}", exist_ok=True)
        input_directory = f"/Users/kunalgupta/Documents/results/{file}/"
        output_file = f"/Users/kunalgupta/Documents/single_sceneprog/{file}/scene.glb"
        merge(input_directory, output_file)
        os.system(f"cp /Users/kunalgupta/Documents/results/{file}/floor.glb /Users/kunalgupta/Documents/single_sceneprog/{file}/floor.glb")
        os.system(f"cp /Users/kunalgupta/Documents/results/{file}/back_wall.glb /Users/kunalgupta/Documents/single_sceneprog/{file}/back.glb")
        render_path = f"/Users/kunalgupta/Documents/single_sceneprog/{file}"
        render(render_path, render_path, 1)
    except Exception as e:
        print(f"Error processing {file}: {str(e)}")

# Example usage
# render('/Users/kunalgupta/Documents/Holodeck/data/scenes/clothing_store_2','/Users/kunalgupta/Documents/Holodeck/data/scenes/clothing_store_2',1)