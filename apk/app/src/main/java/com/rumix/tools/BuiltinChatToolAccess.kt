package com.rumix.tools

object BuiltinChatToolAccess {
    fun registerDefaults() {
        listOf(
            ChatTool(), StatusTool(), TranslateTool(), FilesTool(),
            WakeNeonTool(), ShellTool(), JournalTool(),
        ).forEach { ToolRegistry.register(it) }
    }
}
