import { runShell } from "./shell";
import { readFile, writeFile, listDir, makeDir } from "./files";

export const TOOLS = {
    runShell,
    readFile,
    writeFile,
    listDir,
    makeDir
};

export const TOOL_DEFINITIONS = [
    {
        name: "run_shell",
        description: "Execute a powershell command. Use this for system administration, git, file management, or running apps.",
        parameters: {
            command: { type: "string", description: "The powershell command to execute" }
        }
    },
    {
        name: "read_file",
        description: "Read the contents of a text file.",
        parameters: {
            path: { type: "string", description: "Absolute path to the file" }
        }
    },
    {
        name: "write_file",
        description: "Write content to a file (overwrites existing).",
        parameters: {
            path: { type: "string", description: "Absolute path to the file" },
            content: { type: "string", description: "Text content to write" }
        }
    },
    {
        name: "list_dir",
        description: "List contents of a directory.",
        parameters: {
            path: { type: "string", description: "Absolute path to the directory" }
        }
    }
];
