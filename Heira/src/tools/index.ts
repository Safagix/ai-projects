import { getCurrentTimeTool, getCurrentTime } from './get_current_time.js';
import { runTerminalCommandTool, runTerminalCommand } from './terminal.js';
import { readFileTool, readFile, writeFileTool, writeFile, listDirectoryTool, listDirectory } from './fs.js';
import { readClipboardTool, readClipboard } from './clipboard.js';
import { searchWebTool, searchWeb } from './web.js';
import { launchRegisteredAppTool, launchRegisteredApp, listRegisteredAppsTool, listRegisteredApps, openWebSearchTool, openWebSearch } from './apps.js';
import { saveLearningTool, saveLearningToolHandler } from './learning.js';
import { listDesktopAutomationToolsTool, listDesktopAutomationTools, runAutoHotkeyScriptTool, runAutoHotkeyScript, searchFilesEverythingTool, searchFilesEverything } from './desktop.js';
import { fetchPageWithPlaywrightTool, fetchPageWithPlaywright } from './playwright_browser.js';
import { askLocalModelTool, askLocalModel, localModelStatusTool, localModelStatus } from './local_model.js';

export const availableTools: Record<string, (args: any) => Promise<string>> = {
    [getCurrentTimeTool.function.name]: getCurrentTime,
    [runTerminalCommandTool.function.name]: runTerminalCommand as any,
    [readFileTool.function.name]: readFile as any,
    [writeFileTool.function.name]: writeFile as any,
    [listDirectoryTool.function.name]: listDirectory as any,
    [readClipboardTool.function.name]: readClipboard as any,
    [searchWebTool.function.name]: searchWeb as any,
    [listRegisteredAppsTool.function.name]: listRegisteredApps as any,
    [launchRegisteredAppTool.function.name]: launchRegisteredApp as any,
    [openWebSearchTool.function.name]: openWebSearch as any,
    [saveLearningTool.function.name]: saveLearningToolHandler as any,
    [listDesktopAutomationToolsTool.function.name]: listDesktopAutomationTools as any,
    [searchFilesEverythingTool.function.name]: searchFilesEverything as any,
    [runAutoHotkeyScriptTool.function.name]: runAutoHotkeyScript as any,
    [fetchPageWithPlaywrightTool.function.name]: fetchPageWithPlaywright as any,
    [askLocalModelTool.function.name]: askLocalModel as any,
    [localModelStatusTool.function.name]: localModelStatus as any
};

export const toolsArray = [
    getCurrentTimeTool,
    runTerminalCommandTool,
    readFileTool,
    writeFileTool,
    listDirectoryTool,
    readClipboardTool,
    searchWebTool,
    listRegisteredAppsTool,
    launchRegisteredAppTool,
    openWebSearchTool,
    saveLearningTool,
    listDesktopAutomationToolsTool,
    searchFilesEverythingTool,
    runAutoHotkeyScriptTool,
    fetchPageWithPlaywrightTool,
    askLocalModelTool,
    localModelStatusTool
];
