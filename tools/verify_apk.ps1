# Проверка собранного APK: badging + маркеры содержимого ПРЯМО в assets/ внутри архива.
# Badging не ловит «собралось со старым index.html» — поэтому читаем файлы из zip.
# Запуск: powershell -File tools\verify_apk.ps1 [-Expect 'маркер1','маркер2']
param([string[]]$Expect = @())
$apk = Join-Path $PSScriptRoot '..\HeshbonPlus.apk'
$aapt = (Get-ChildItem 'C:\Users\Katan\android-build\sdk\build-tools' -Recurse -Filter 'aapt2.exe' | Select-Object -First 1).FullName

Write-Output '---- badging:'
cmd /c "`"$aapt`" dump badging `"$apk`" 2>&1" | Select-String -Pattern '^package|^application-label:'

Add-Type -AssemblyName System.IO.Compression.FileSystem
$zip = [System.IO.Compression.ZipFile]::OpenRead($apk)
Write-Output '---- содержимое:'
$zip.Entries | Where-Object { $_.FullName -like 'assets/*' -or $_.FullName -eq 'classes.dex' } |
  ForEach-Object { '   {0,-24} {1,8} байт' -f $_.FullName, $_.Length }
function Read-Entry($z, $name) {
  $e = $z.GetEntry($name); if (-not $e) { return '' }
  $sr = New-Object System.IO.StreamReader($e.Open()); $t = $sr.ReadToEnd(); $sr.Close(); return $t
}
$html = Read-Entry $zip 'assets/index.html'
$i18n = Read-Entry $zip 'assets/i18n.js'
$zip.Dispose()

# базовые маркеры + переданные через -Expect (ищутся и в html, и в словаре)
$checks = [ordered]@{
  'APP_VERSION совпадает с манифестом' = $true
}
if ($html -match "APP_VERSION = '([^']+)'") { $appv = $matches[1] } else { $appv = '?' }
$man = Get-Content 'C:\Users\Katan\android-build\app\AndroidManifest.xml' -Raw
if ($man -match 'versionName="([^"]+)"') { $manv = $matches[1] } else { $manv = '?' }
$checks['APP_VERSION совпадает с манифестом'] = ($appv -eq $manv)
foreach ($e in $Expect) { $checks["маркер: $e"] = ($html.Contains($e) -or $i18n.Contains($e)) }

Write-Output ("---- маркеры (APP_VERSION={0}, manifest={1}):" -f $appv, $manv)
foreach ($k in $checks.Keys) { '   {0}  {1}' -f $(if ($checks[$k]) { 'OK ' } else { 'НЕТ' }), $k }
$bad = ($checks.Values | Where-Object { -not $_ }).Count
if ($bad) { Write-Output ('!!! ПРОВАЛЕНО ПРОВЕРОК: ' + $bad); exit 1 } else { Write-Output 'Все проверки пройдены — APK можно отправлять' }
