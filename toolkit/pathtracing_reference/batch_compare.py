"""

Compares various results

"""

from __future__ import print_function

import os
import sys
import shutil

from panda3d.core import PNMImage

try:
    os.makedirs("batch_compare")
except:
    pass

overlay = PNMImage("res/overlay.png")

materials_to_test = []

GOLD_F0 = (1, 0.867136, 0.358654)

# materials_to_test.append({
#         "name": "Gold",
#         "basecolor": GOLD_F0,
#         "roughness": 0.1,
#         "type": "metallic",
#         "material_src": "Au"
#     })

# materials_to_test.append({
#         "name": "Foliage",
#         "basecolor": (0.6, 0.9, 0.6),
#         "roughness": 0.6,
#         "type": "foliage"
#     })

# materials_to_test.append({
#         "name": "GoldRough",
#         "basecolor": GOLD_F0,
#         "roughness": 0.4,
#         "type": "metallic",
#         "material_src": "Au"
#     })


# materials_to_test.append({
#         "name": "Test-R0",
#         "basecolor": (0, 0, 0),
#         "ior": 1.51,
#         "roughness": 0.3
#     })

# materials_to_test.append({
#         "name": "Test-IOR1.1",
#         "basecolor": (0, 0, 1),
#         "ior": 1.1,
#         "roughness": 0.0
#     })

# materials_to_test.append({
#         "name": "Test-IOR2",
#         "basecolor": (0, 0, 1),
#         "ior": 2.0,
#         "roughness": 0.0
#     })

# materials_to_test.append({
#         "name": "Test-IOR2.5",
#         "basecolor": (0, 0, 1),
#         "ior": 2.5,
#         "roughness": 0.0
#     })


# materials_to_test.append({
#         "name": "Test-SpecOnly",
#         "basecolor": (0, 0, 0),
#         "ior": 1.5,
#         "roughness": 0.0
#     })

# materials_to_test.append({
#         "name": "Test-SpecOnly-R0.3",
#         "basecolor": (0, 0, 0),
#         "ior": 1.5,
#         "roughness": 0.3
#     })

# materials_to_test.append({
#         "name": "Nonrefractive-Diffuse",
#         "basecolor": (0.5, 0.5, 0.5),
#         "ior": 1.0,
#         "roughness": 1.0
#     })

# materials_to_test.append({
#         "name": "Rough-Diffuse",
#         "basecolor": (0.5, 0.5, 0.5),
#         "ior": 1.5,
#         "roughness": 0.8
#     })
# materials_to_test.append({
#         "name": "Normal-Diffuse",
#         "basecolor": (00.5, 0.5, 0.5),
#         "ior": 1.5,
#         "roughness": 0.4
#     })


for i in range(11):
    roughness = i / 10.0
    
    materials_to_test.append({
            "name": "Plastic-R" + str(roughness),
            "basecolor": (1, 0, 0),
            "ior": 1.51,
            "roughness": roughness
        })
    
    # materials_to_test.append({
    #         "name": "Gold-R" + str(roughness),
    #         "basecolor": GOLD_F0,
    #         "ior": 1.51,
    #         "type": "metallic",
    #         "material_src": "Au",
    #         "roughness": roughness
    #     })

    # materials_to_test.append({
    #         "name": "Clearcoat-R" + str(roughness),
    #         "basecolor": (1, 0.85, 0.345),
    #         "material_src": "Au",
    #         "type": "clearcoat",
    #         "roughness": roughness
    #     })

    # materials_to_test.append({
    #         "name": "Diffuse-R" + str(roughness),
    #         "basecolor": (0.8, 0.8, 0.8),
    #         "ior": 1.16,
    #         "roughness": roughness
    #     })


for material in materials_to_test:

    print("Testing material", material["name"])

    # Write material def
    with open("_tmp_material.py", "w") as handle:
        handle.write("# Autogenerated\n")
        handle.write("name = '{}'".format(material["name"]) + "\n")
        handle.write("roughness = {}".format(material["roughness"]) + "\n")
        handle.write("ior = {}".format(material.get("ior", 1.51)) + "\n")
        handle.write("basecolor = {}".format(material["basecolor"]) + "\n")
        handle.write("mat_type = '{}'".format(material.get("type", "default")) + "\n")

    # run rp
    print("  Running RP ..")
    cmd = '"{}"'.format(sys.executable) + " -B run_renderpipeline.py silent > nul"
    os.system(cmd)

    print("  Running mitsuba ..")
    # run mitsuba
    with open("res/scene.templ.xml", "r") as handle:
        content = handle.read()

    mat_type = material.get("type", "default")

    use_default = mat_type == "default"
    use_metallic = mat_type == "metallic"

    for shading_type in (("default", "metallic", "clearcoat")):
        def_name = shading_type.upper()
        if mat_type == shading_type:
            content = content.replace("%IF_" + def_name + "%", "")
            content = content.replace("%ENDIF_" + def_name + "%", "")
        else:
            content = content.replace("%IF_" + def_name + "%", "<!--")
            content = content.replace("%ENDIF_" + def_name + "%", "-->")

    content = content.replace("%ALPHA%", str(material["roughness"] * material["roughness"]))
    content = content.replace("%IOR%", str(material.get("ior", 1.51)))
    content = content.replace("%BASECOLOR%", str(material["basecolor"]).strip("()"))
    content = content.replace("%MATERIAL_SRC%", material.get("material_src", "").strip("()"))


    with open("res/scene.xml", "w") as handle:
        handle.write(content)

    os.system("run_mitsuba.bat > nul")

    print("  Writing result ..")
    img = PNMImage("scene-rp.png")
    img_ref = PNMImage("scene.png")

    img.copy_sub_image(img_ref, 256, 0, 256, 0, 256, 512)
    img.mult_sub_image(overlay, 0, 0)
    img.write("batch_compare/" + material["name"] + ".png")

try:
    os.remove("_tmp_material.py")
except:
    pass

print("Done!")
