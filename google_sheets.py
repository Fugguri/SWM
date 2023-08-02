import gspread
import datetime

class GS ():
    
    def __init__(self) -> None:
        self.gs = gspread.service_account(
            filename='brave-design-383019-841912aaeec5.json')
    
    def sheets_append_row(self, sheet_name, username, number, request,answer):
        sh = self.gs.open(sheet_name)
        worksheet = sh.get_worksheet(0)
        date = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
        values = ([date, username, number, request,answer])
        worksheet.append_row(values=values)
if __name__ == "__main__":
    a=GS()
    a.sheets_append_row("gpt",'event.chat_id',
                                'phone',
                                's',
                                'answer')