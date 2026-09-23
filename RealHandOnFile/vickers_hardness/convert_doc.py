"""Use Word COM to extract text properly."""
import os
import sys

doc_path = r"e:\latex_AI\RealHandOnFile\vickers_hardness\data\24012720(2).doc"
txt_path = r"e:\latex_AI\RealHandOnFile\vickers_hardness\data\output_unicode.txt"

# Use Word COM via Python
import subprocess
ps_script = f'''
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$doc = $word.Documents.Open("{doc_path}")
$doc.SaveAs([ref]"{txt_path}", [ref]5)  # 5 = Unicode Text
$doc.Close()
$word.Quit()
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null
Write-Host "Saved as Unicode text"
'''

# Write and run PowerShell
ps_file = r"e:\latex_AI\RealHandOnFile\vickers_hardness\data\convert.ps1"
with open(ps_file, 'w', encoding='utf-8') as f:
    f.write(ps_script)

result = subprocess.run(['powershell', '-ExecutionPolicy', 'Bypass', '-File', ps_file], 
                       capture_output=True, text=True)
print(result.stdout)
print(result.stderr)

# Read the unicode text file
if os.path.exists(txt_path):
    with open(txt_path, 'r', encoding='utf-16') as f:
        content = f.read()
    print("=== Document Content ===")
    print(content[:5000])
    print("=== End ===")
else:
    print("Output file not found")
