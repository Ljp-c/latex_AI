$ErrorActionPreference = "Continue"
$eds = "E:\latex_AI\纳米材料制备与表征\课程论文\analysis\data\sem\SEM专业实验-2024级（包含EDS）\EDS 1-10组\eds"
$out = "E:\latex_AI\纳米材料制备与表征\课程论文\analysis\outputs"
$docs = @("$eds\7\TiO.doc", "$eds\8\8#.doc")
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
$i = 0
foreach ($d in $docs) {
    $i++
    $pdf = Join-Path $out ("eds_report_$i.pdf")
    $doc = $word.Documents.Open($d, $false, $true, $false)
    Write-Output ("pages=" + $doc.ComputeStatistics(2))
    $doc.SaveAs2($pdf, 17)
    $doc.Close($false)
    Write-Output ("saved " + $pdf)
}
$word.Quit()
