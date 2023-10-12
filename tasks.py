from robocorp.tasks import task
from robocorp import browser
import time

from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive
@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt
    Creates ZIP archive of the receipts and the images.
    """
    browser.configure(
        browser_engine="chrome",
    )
    orders = get_orders()
    open_robot_order_website()    
    for row in orders:
        order_number = row['Order number']
        close_annoying_modal()
        fill_the_form(row)
        screenshot = preview_and_screenshot_robot(order_number)
        submit_order_and_check_for_error()
        pdf_file = store_receipt_as_pdf(order_number)
        embed_screenshot_to_receipt(screenshot, pdf_file)
    archive_receipts()


    

def open_robot_order_website():
    """Opens the robot order website in chrome."""
    browser.goto("https://robotsparebinindustries.com/#/robot-order/")

def get_orders():
    """Downloads the orders csv file."""
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)
    tables = Tables()
    table = tables.read_table_from_csv("orders.csv")
    data_list = [row for row in table]
    return data_list

def close_annoying_modal():
    page = browser.page()
    page.click("button:text('OK')")

def fill_the_form(row):
    page = browser.page()
    page.select_option("#head", str(row["Head"]))
    page.click("#id-body-" + str(row["Body"]))
    legs = page.wait_for_selector("input[placeholder='Enter the part number for the legs']")
    legs.fill(str(row['Legs']))
    page.fill("#address", str(row["Address"]))

def preview_and_screenshot_robot(order_number):
    page = browser.page()
    page.click("button:text('Preview')")
    image = page.locator("#robot-preview-image")
    time.sleep(0.5)
    image.screenshot(path= "pngs/" + str(order_number) + "robot.png")
    screenshot = "pngs/" + str(order_number) + "robot.png"
    return screenshot
    
def submit_order_and_check_for_error():
    page = browser.page()
    page.click("button:text('ORDER')")
    alert = page.query_selector("#receipt")
    if alert is None:
        submit_order_and_check_for_error()

def store_receipt_as_pdf(order_number):
    page = browser.page()
    pdf = PDF()
    receiptelement = page.locator("#receipt")
    receipt = receiptelement.inner_html()
    pdf.html_to_pdf(receipt, "pdfs/" + str(order_number) + ".pdf")
    file = "pdfs/" + str(order_number) + ".pdf"
    page.click("button:text('ORDER ANOTHER ROBOT')")
    return file

def embed_screenshot_to_receipt(screenshot, pdf_file):
    pdf = PDF()
    pdf.add_files_to_pdf([screenshot], pdf_file, True)

def archive_receipts():
    zip = Archive()
    zip.archive_folder_with_zip("pdfs", "zipped_receipts.zip")
    


