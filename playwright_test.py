from dataclasses import field

from playwright.sync_api import Page, sync_playwright


def inspect_fields():

    # Initialize Playwright and launch a browser using with context manager to ensure proper cleanup
    with sync_playwright() as p:
        # Launch chromium browser in non-headless mode to see the actions being performed
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://httpbin.org/forms/post")
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

            label = label_matching(field, page)
            print(field_dict.get("id"), field_dict.get("name"), "->", label)
            # Add field info to the list
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


if __name__ == "__main__":
        inspect_fields()
    