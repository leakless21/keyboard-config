#Requires AutoHotkey v2.0
#SingleInstance Force

; =============================================================================
; Keyboard Semantic Host Bridge for Windows (AutoHotkey v2)
;
; Translates semantic F13-F24 signals from NAV/MOUSE/HOST layers into standard
; Windows clipboard, application, launcher, terminal, and window shortcuts.
;
; Keyboard emits:                Windows receives:
;   Hyper+F13                  ->    Ctrl+A         (Select All)
;   Hyper+F14                  ->    Ctrl+S         (Save)
;   Hyper+F15                  ->    Ctrl+F         (Find)
;   Hyper+F16                  ->    Ctrl+Shift+Tab (Previous Tab)
;   Hyper+F17                  ->    Ctrl+Tab       (Next Tab)
;   Hyper+F18                  ->    Ctrl+T         (New Tab)
;   Hyper+F19                  ->    Ctrl+W         (Close Tab)
;   Hyper+F20                  ->    Ctrl+Shift+T   (Reopen Closed Tab)
;   Hyper+F21                  ->    Ctrl+Left      (Word Left)
;   Hyper+F22                  ->    Ctrl+Right     (Word Right)
;   Hyper+F23                  ->    F3             (Find Next)
;   Hyper+F24                  ->    Ctrl+Y         (Redo)
;   F21 (with held mods)       ->    Ctrl+C         (Copy)
;   F22 (with held mods)       ->    Ctrl+V         (Paste)
;   F23 (with held mods)       ->    Ctrl+X         (Cut)
;   F24 (with held mods)       ->    Ctrl+Z         (Undo)
;   Alt+F13                    ->    Win+S          (System Launcher / Windows Search)
;   Alt+F14                    ->    Ctrl+Alt+`     (Quick Terminal / Quake summon)
;   Alt+F15                    ->    Run wt.exe     (New independent Windows Terminal)
;   Alt+F16                    ->    Alt+Tab        (Previous Window)
;   Alt+F17                    ->    EVKey toggle   (Language Toggle)
; =============================================================================

; -----------------------------------------------------------------------------
; Application & Navigation Actions (Hyper = Ctrl+Alt+Shift+Win)
; -----------------------------------------------------------------------------
^!+#F13::Send("^a")
^!+#F14::Send("^s")
^!+#F15::Send("^f")
^!+#F16::Send("^+{Tab}")
^!+#F17::Send("^{Tab}")
^!+#F18::Send("^t")
^!+#F19::Send("^w")
^!+#F20::Send("^+t")
^!+#F21::Send("^{Left}")
^!+#F22::Send("^{Right}")
^!+#F23::Send("{F3}")
^!+#F24::Send("^y")

; -----------------------------------------------------------------------------
; Semantic Clipboard & Editing (Tolerates extra held modifiers)
; -----------------------------------------------------------------------------
*F21::Send("^c")
*F22::Send("^v")
*F23::Send("^x")
*F24::Send("^z")

; -----------------------------------------------------------------------------
; Desktop Actions & Launchers (HOST Layer)
; -----------------------------------------------------------------------------
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
