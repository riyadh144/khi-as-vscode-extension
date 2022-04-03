from click import command
import pyexcel_ods3 as pe
import json

wb = pe.get_data("Kawasaki_AS_language_keyword_and_structures.ods")
command_structure = {}
section_lookup = {}
cmd_type_lookup = {}
# first we create the our categories
# we start with command types
for i, cmd_type_row in enumerate(wb["CommandTypes"]):
    if i > 0 and len(cmd_type_row) > 0:
        cmd_type = cmd_type_row[1].replace(" ", "-").lower()
        command_structure[cmd_type] = {}
        cmd_type_lookup[cmd_type_row[0]] = cmd_type

for i, section_row in enumerate(wb["Sections"]):
    if i > 0 and len(section_row) > 0:
        section = section_row[1].replace(" ", "-").lower()
        for entry in command_structure:
            command_structure[entry][section] = []
        section_lookup[section_row[0]] = section

# print(section_lookup)

# Now we populate the structure
for i, command_row in enumerate(wb["CommandAppendix"]):
    try:
        if i > 0 and len(command_row) > 0:
            og_command = command_row[0]
            abv_command = command_row[1]
            list_to_extend = []
            if og_command != abv_command:
                list_to_extend = [og_command, abv_command]
            else:
                list_to_extend = [og_command]
            if i > 0 and len(command_row) > 0:
                command_structure[cmd_type_lookup[command_row[3]]][
                    section_lookup[str(command_row[5])]
                ].extend(list_to_extend)

    except IndexError as e:

        print(
            f"A non empty row with no appendinx {i+1} {command_row} in Command Appendix"
        )

# Now we use the structure to create our regex
# I would like it to be in the following form
# {
# 	"match": "\\b(?i)(pcstatus|pcexecute|pckill|pcabort|pcend|pccontinue|pcstep|pcscan)\\b",
# 	"name": "keyword.control.process.open-as"
# },
with open("dump_regex.txt", "w+") as file:
    for cmd_type in command_structure:
        for cmd_section in command_structure[cmd_type]:
            regex = "\\\\b(?i)("
            valid = 0
            for command_ in command_structure[cmd_type][cmd_section]:
                valid = 1
                regex = regex + str(command_) + "|"

            regex = regex[:-1] + ")\\\\b"

            if valid == 1:
                name = f'"name": "keyword.{cmd_type}.{cmd_section}.open-as"'
                match = f'"match": "{regex}"'
                full_string = "{\n" + match + ",\n" + name + "\n},\n"
                file.write(full_string)
                print(full_string)
