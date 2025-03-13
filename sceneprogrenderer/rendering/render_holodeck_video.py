def render(glb_directory, output_directory, downsample=1):
    with open('holodeck_params.txt', 'w') as f:
        f.write(glb_directory + '\n')
        f.write(output_directory + '\n')
        f.write(str(downsample) + '\n')

    import subprocess

    blender_executable_path = '/Applications/Blender.app/Contents/MacOS/Blender'
    script_path = '/Users/kunalgupta/Documents/rendering/worker_holodeck_render_video.py'

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
for file in os.listdir('/Users/kunalgupta/Documents/Holodeck/data/scenes'):
    try:
        if '.DS_Store' in file:
            continue
        
        input_directory = f"/Users/kunalgupta/Documents/Holodeck/data/scenes/{file}/output/"
        output_file = f"/Users/kunalgupta/Documents/Holodeck/data/scenes/{file}/scene.glb"
        merge(input_directory, output_file)
        render_path = f"/Users/kunalgupta/Documents/Holodeck/data/scenes/{file}"
        render(render_path, render_path, 1)
    except Exception as e:
        print(f"Error processing {file}: {str(e)}")
# Example usage
# render('/Users/kunalgupta/Documents/Holodeck/data/scenes/clothing_store_2','/Users/kunalgupta/Documents/Holodeck/data/scenes/clothing_store_2',1)