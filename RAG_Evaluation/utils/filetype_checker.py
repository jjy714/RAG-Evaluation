from pathlib import Path



def filetype_checker(file_name: str):
    Path(file_name).suffix == '.pdf'    
    Path(file_name).suffix == '.csv'    
    Path(file_name).suffix == '.docx'    
    Path(file_name).suffix == '.doc'    
    pass