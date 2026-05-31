# Security Check List (SCL): Eira App

## 🔒 Data Protection

- [ ] **Local Only**: Ensure no user data (Notes, Habits) is sent to external servers unless the user interacts with the LLM.
- [ ] **API Secrecy**: API Keys (OpenRouter, Gemini) must remain in the `.env` or highly restricted config files.
- [ ] **Sanitization**: All HTML/Markdown rendered from notes must be sanitized to prevent XSS within the webview.

## 🛡️ Tauri Permissions

- [ ] **FS Scope**: Limit `tauri-plugin-fs` scope to the user's `$APP_DATA` and `SkillLibrary` folders only.
- [ ] **Shell Control**: Ensure `shell-execute` is restricted to known binaries (powershell/cmd).

## 🚀 Quality Assurance

- [ ] **Conflict Resolution**: Check for write conflicts if multiple instances try to auto-save JSON files.
