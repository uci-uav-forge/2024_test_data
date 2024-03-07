# converts yolov8 format into irl_dataset format

import os
import shutil
import yaml


if __name__ == "__main__":
    # step 1: get list of tuples (img_path, label_path)
    in_dir = "test"
    out_dir = "irl_dataset"
    os.makedirs(f"{out_dir}/images", exist_ok=True)
    os.makedirs(f"{out_dir}/labels", exist_ok=True)
    img_names = os.listdir(f"{in_dir}/images")
    label_names = os.listdir(f"{in_dir}/labels")
    img_label_pairs = list(zip(sorted(img_names), sorted(label_names)))

    # step 2: convert label files to irl_dataset format
    # read class names from yaml file
    with open("data.yaml", "r") as f:
        yaml_file = yaml.safe_load(f)
        class_names: list[str] = yaml_file["names"]


    i = 0
    for img_name, label_name in img_label_pairs:
        with open(f"{in_dir}/labels/{label_name}", "r") as f:
            lines: list[str] = f.readlines()
            for i, line in enumerate(lines):
                class_index, x, y, w, h = line.split()
                class_name = class_names[int(class_index)]
                new_line = f'{class_name.replace("-",",")} {x} {y} {w} {h}'
                # if num commas is between 1 and 3 inclusive, it's invalid
                if 1 <= new_line.count(",") < 3:
                    print(f"Invalid label file (weird number of commas): {label_name}")
                    print(f"Offending line: {new_line}")
                lines[i] = new_line

            # if no lines contain a comma, they don't have the new multi-class format, so mark the file for deletion
            if any(
                ["," not in line and "person" not in line for line in lines]
            ):
                print(f"Invalid label file: {label_name}")
                continue
        
        with open(f"{out_dir}/labels/image{i}.txt", "w") as f:
            f.writelines('\n'.join(lines))
        
        shutil.copyfile(f"{in_dir}/images/{img_name}", f"{out_dir}/images/image{i}.png")
        i+=1


