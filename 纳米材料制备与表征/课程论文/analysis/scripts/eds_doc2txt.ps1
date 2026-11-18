$ErrorActionPreference = "Continue"
$eds = "E:\latex_AI\纳米材料制备与表征\课程论文\analysis\data\sem\SEM专业实验-2024级（包含EDS）\EDS 1-10组\eds"
$out = "E:\latex_AI\纳米材料制备与表征\课程论文\analysis\outputs"
New-Item -ItemType Directory -Force -Path $out | Out-Null
$docs = @("$eds\7\TiO.doc", "$eds\8\8#.doc", "$eds\9\Doc9.doc", "$eds\3-2#\Doc4.doc", "$eds\10\10#.doc")
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
$i = 0
foreach ($d in $docs) {
    $i++
    if (-not (Test-Path -LiteralPath $d)) { Write-Output "missing $d"; continue }
    try {
        $doc = $word.Documents.Open($d, $false, $true, $false)
        $name = "eds_doc_$i.txt"
        [System.IO.File]::WriteAllText((Join-Path $out $name), $doc.Content.Text, (New-Object System.Text.UTF8Encoding($true)))
        Write-Output ("$name <- " + [System.IO.Path]::GetFileName($d) + " chars=" + $doc.Content.Text.Length)
        $doc.Close($false)
    } catch { Write-Output ("FAIL " + $d + " : " + $_.Exception.Message) }
}
$word.Quit()
Write-Output "done"
