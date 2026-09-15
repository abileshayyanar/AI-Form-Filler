from dataclasses import field
from playwright.sync_api import Page, sync_playwright
import json
import requests

# Good test URL: https://httpbin.org/forms/post

def inspect_fields():

    # Initialize Playwright and launch a browser using with context manager to ensure proper cleanup
    with sync_playwright() as p:
        # Launch firefox browser in non-headless mode to see the actions being performed
        browser = p.firefox.launch(headless=False)
        page = browser.new_page()
        page.goto("https://httpbin.org/forms/post")  # Replace with the actual URL you want to inspect
        # Find all form fields (input, select, textarea) on the page
        fields = page.query_selector_all("input, select, textarea")

        # Initialize empty list to hold fields information
        fields_info = []
        for field in fields:
            # Create new dictionary to hold info about each field
            field_dict = {}
            # Populate the dictionary with field attributes if they exist
            if field.get_attribute("id"):
                field_dict["id"] = field.get_attribute("id")
            if field.get_attribute("name"):
                field_dict["name"] = field.get_attribute("name")
            if field.get_attribute("type"):
                field_dict["type"] = field.get_attribute("type")
            if field.get_attribute("placeholder"):
                field_dict["placeholder"] = field.get_attribute("placeholder")

            # Get the HTML tag associated with the field
            field_dict["tag"] = field.evaluate("el => el.tagName")

            # Build the selector based on the field's attributes
            if field_dict.get("id"):
                field_dict["selector"] = f'#{field_dict["id"]}'
            else:
                field_dict["selector"] = f'{field_dict["tag"].lower()}[name="{field_dict.get("name")}"]'

            label = label_matching(field, page)
            # Remove whitespace if label is not None
            if label:
                label = label.strip()
            print(field_dict.get("id"), field_dict.get("name"), "->", label)

            value = field.get_attribute("value")
            # Check for radio buttons and checkboxes to group them by name and collect their labels
            if field_dict.get("type") in ("radio", "checkbox"):
                # Iterate through each existing entry
                for existing_entry in fields_info:
                    # If the name matches, append the label to the options list
                    if existing_entry.get("name") == field_dict.get("name"):
                        existing_entry["options"].append({"label": label, "value": value})
                        break
                # If no existing entry was found, create a new entry with the label in the options list
                else:
                    field_dict["options"] = [{"label": label, "value": value}]
                    fields_info.append(field_dict)        
            else:
                # Automatically add field info to the list if it's not a radio button or checkbox
                fields_info.append(field_dict)

        browser.close()
        print(fields_info)
        return fields_info


def label_matching(field, page):
    field_id = field.get_attribute("id")

    # Step 1: Check if there is an explicit label associated with the field using the 'for' attribute
    if field_id:        
        label_element = page.query_selector(f'label[for="{field_id}"]')
        if label_element:
            return label_element.inner_text()

    # Step 2: If no explicit label is found, check if the field is wrapped inside a label element
    step_2_label = field.evaluate("el => { const lbl = el.closest('label'); return lbl ? lbl.innerText : null; }")
    if step_2_label:
        return step_2_label

    # Step 3: If still no label is found, check for aria-label or placeholder attributes
    step_3_label= field.get_attribute("aria-label")
    if step_3_label:
        return step_3_label
    else:
        return field.get_attribute("placeholder")


def create_prompt(fields_json, profile_json):
    # Create a prompt for the AI model using the fields and profile data
    prompt = f"""
    You are an AI assistant that helps fill out job application forms based on the user's resume information.
    Here are the form fields extracted from the webpage:
    {fields_json}

    Here is the user's profile data:
    {profile_json}
    """
    return prompt


if __name__ == "__main__":
    fields_json = json.dumps(inspect_fields(), indent=4)
    # Read provided JSON file containing profile data as string
    with open("profile_data.json") as f:
        profile_json = f.read()