const clients = workspace.clientList();
const clientsCapture = {};

clients.forEach((client) => {
  if (client.specialWindow)
    return;
  clientsCapture[client.caption] = {
    "desktop": client.desktop,
    "activities": client.activities
  };
});

callDBus("org.kde.KWin.Script.WindowRestore", "/WindowRestore", "org.kde.kwin.Script", "Save", JSON.stringify(clientsCapture));

callDBus("org.kde.KWin.Script.WindowRestore", "/WindowRestore", "org.kde.kwin.Script", "UnloadServiceScript");
