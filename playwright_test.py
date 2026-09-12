from playwright.sync_api import Page, sync_playwright


def inspect_fields():

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("[APPLICATION URL]")
        fields = page.query_selector_all("input, select, textarea")

        fields_info = []
        for field in fields:
            field_dict = {}
            if field.get_attribute("id"):
                field_dict["id"] = field.get_attribute("id")
            if field.get_attribute("name"):
                field_dict["name"] = field.get_attribute("name")
            if field.get_attribute("type"):
                field_dict["type"] = field.get_attribute("type")
            if field.get_attribute("placeholder"):
                field_dict["placeholder"] = field.get_attribute("placeholder")
            field_dict["tag"] = field.evaluate("el => el.tagName")

            fields_info.append(field_dict)

        browser.close()
        return fields_info

def label_matching(field, page):
    label[for="{field.get_attribute('id')}"]')
    