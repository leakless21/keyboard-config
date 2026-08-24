#Requires AutoHotkey v2.0
#SingleInstance Force

; =============================================================================
; Keyboard Semantic Host Bridge for Windows (AutoHotkey v2)
;
; Translates semantic F13-F24 signals from NAV/MOUSE/HOST layers into standard
; Windows clipboard, launcher, terminal, and window shortcuts.
;
; Keyboard emits:      Windows receives:
;   F21            ->    Ctrl+C         (Copy)
;   F22            ->    Ctrl+V         (Paste)
;   F23            ->    Ctrl+X         (Cut)
;   F24            ->    Ctrl+Z         (Undo)
;   Shift+F24      ->    Ctrl+Y         (Redo)
;   Alt+F13        ->    Win+S          (System Launcher / Windows Search)
;   Alt+F14        ->    Ctrl+Alt+`     (Quick Terminal / Quake summon)
;   Alt+F15        ->    Run wt.exe     (New independent Windows Terminal)
;   Alt+F16        ->    Alt+Tab        (Previous Window)
;   Alt+F17        ->    EVKey toggle   (Language Toggle)
; =============================================================================

; Redo (Shift+F24) must precede bare F24
+F24::Send("^y")

; Undo (F24)
F24::Send("^z")

; Copy (F21)
F21::Send("^c")

; Paste (F22)
F22::Send("^v")

; Cut (F23)
F23::Send("^x")

; System Launcher (Alt+F13 -> Win+S / Windows Search)
!F13::Send("#s")

; Quick Terminal summon/toggle (Alt+F14 -> Ctrl+Alt+` matching Windows Terminal action)
!F14::Send("^!``")

; New Terminal window (Alt+F15 -> launch standard Windows Terminal in workspace)
!F15::Run("wt.exe")

; Previous Window toggle (Alt+F16 -> Alt+Tab)
!F16::Send("!{Tab}")

; Language Toggle (Alt+F17 -> EVKey E/V toggle)
; EVKey must use the same E/V toggle shortcut configured below.
ToggleInputLanguage() {
    SendEvent("{Ctrl down}{Shift down}{Shift up}{Ctrl up}")
}

!F17::ToggleInputLanguage()
