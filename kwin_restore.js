const workspaceClients = workspace.clientList();

callDBus("org.kde.KWin.Script.WindowRestore", "/WindowRestore", "org.kde.kwin.Script", "Restore", (savedClientsJson) => {
    const savedClients = JSON.parse(savedClientsJson);
    workspaceClients.forEach((client) => {
        const savedClient = savedClients[client.caption];
        if (!savedClient)
            return;
        client.desktop = savedClient.desktop;
        client.activities = savedClient.activities;
    });
    callDBus("org.kde.KWin.Script.WindowRestore", "/WindowRestore", "org.kde.kwin.Script", "UnloadServiceScript");
});
