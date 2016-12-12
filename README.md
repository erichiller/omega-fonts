[Windows Portable builds](http://fontforgebuilds.sourceforge.net/)


[FontForge native builds & Windows Installers](http://fontforge.github.io/en-US/downloads/windows-dl/)

Usage, from the project's root:

	.\fontforge\bin\fontforge.exe -script .\patcher\font-patcher.py --windows --powerline --octicons -out .\fonts-out\ .\fonts-src\dejavu-fonts-ttf-2.37\ttf\DejaVuSansMono-Oblique.ttf

Sources:

[Hack](https://github.com/chrissimpkins/Hack)

[Octicons](https://github.com/primer/octicons)

_Consolas must be provided by your computer_




$sl = $global:ThemeSettings #local settings

$sl.PromptSymbols.StartSymbol                       = [char]::ConvertFromUtf32(0x03a9)      # Standard , greek omega

$sl.PromptSymbols.ElevatedSymbol                    = [char]::ConvertFromUtf32(0xf0e7)      # Lightning     #26A1
$sl.PromptSymbols.FailedCommandSymbol               = [char]::ConvertFromUtf32(0xf468)      # octicons		#f081


### THESE ARE IN **REGULAR** POWERLINE -- SAME
$sl.PromptSymbols.SegmentForwardSymbol              = [char]::ConvertFromUtf32(0xE0B0)      # Filled arrow right; powerline
$sl.PromptSymbols.SegmentBackwardSymbol             = [char]::ConvertFromUtf32(0xE0B2)      # filled arrow left; powerline
$sl.PromptSymbols.SegmentSeparatorForwardSymbol     = [char]::ConvertFromUtf32(0xE0B1)      # empty arrow right; powerline
$sl.PromptSymbols.SegmentSeparatorBackwardSymbol    = [char]::ConvertFromUtf32(0xE0B3)      # empty arrow left powerline

$sl.GitSymbols.BranchSymbol                         = [char]::ConvertFromUtf32(0xf418)      # octicons		#f020
$sl.GitSymbols.BranchUntrackedSymbol                = [char]::ConvertFromUtf32(0x2A2F)      # Standard
$sl.GitSymbols.BranchIdenticalStatusToSymbol        = [char]::ConvertFromUtf32(0x2261)      # Standard
$sl.GitSymbols.BranchAheadStatusSymbol              = [char]::ConvertFromUtf32(0xf47c)      # octicons		#f0a2
$sl.GitSymbols.BranchBehindStatusSymbol             = [char]::ConvertFromUtf32(0xf47d)      # octicons		#f0a3

