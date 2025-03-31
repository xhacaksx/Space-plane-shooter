import React, { useEffect, useRef } from "react";
import { Editor } from "@monaco-editor/react";
import * as Y from "yjs";
import { WebsocketProvider } from "y-websocket";
import { io, Socket } from "socket.io-client";
import { MonacoBinding } from "y-monaco";

interface CursorData {
  userId: string;
  position: {
    lineNumber: number;
    column: number;
  };
}

const CollaborativeEditor: React.FC = () => {
  const editorRef = useRef<any>(null);
  const socketRef = useRef<Socket | null>(null);
  const yDocRef = useRef<Y.Doc | null>(null);
  const providerRef = useRef<WebsocketProvider | null>(null);

  useEffect(() => {
    // Initialize Y.js document
    const yDoc = new Y.Doc();
    const yText = yDoc.getText("monaco");
    yDocRef.current = yDoc;

    // Connect to Y.js WebSocket server
    const wsProvider = new WebsocketProvider(
      "ws://localhost:4000/yjs",
      "monaco-demo",
      yDoc
    );
    providerRef.current = wsProvider;

    // Connect to Socket.IO for cursor awareness
    const socket = io("http://localhost:4000");
    socketRef.current = socket;

    // Handle cursor updates from other users
    socket.on("cursor-update", (data: CursorData) => {
      if (editorRef.current) {
        const model = editorRef.current.getModel();
        if (!model) return;

        // Add or update remote cursor decoration
        const decorations = model.deltaDecorations(
          [],
          [
            {
              range: {
                startLineNumber: data.position.lineNumber,
                startColumn: data.position.column,
                endLineNumber: data.position.lineNumber,
                endColumn: data.position.column + 1,
              },
              options: {
                className: "remote-cursor",
                hoverMessage: { value: `Cursor: ${data.userId}` },
              },
            },
          ]
        );
      }
    });

    return () => {
      // Cleanup
      if (socketRef.current) {
        socketRef.current.disconnect();
      }
      if (providerRef.current) {
        providerRef.current.destroy();
      }
      if (yDocRef.current) {
        yDocRef.current.destroy();
      }
    };
  }, []);

  const handleEditorDidMount = (editor: any) => {
    editorRef.current = editor;

    // Initialize Monaco binding with Y.js
    if (yDocRef.current) {
      new MonacoBinding(
        yDocRef.current.getText("monaco"),
        editor.getModel(),
        new Set([editor]),
        providerRef.current?.awareness
      );
    }

    // Send cursor position updates
    editor.onDidChangeCursorPosition((e: any) => {
      if (socketRef.current) {
        socketRef.current.emit("cursor-update", {
          position: {
            lineNumber: e.position.lineNumber,
            column: e.position.column,
          },
        });
      }
    });
  };

  return (
    <div style={{ height: "100vh", width: "100%" }}>
      <Editor
        height="100%"
        defaultLanguage="javascript"
        defaultValue="// Start coding here..."
        onMount={handleEditorDidMount}
        options={{
          minimap: { enabled: false },
          fontSize: 16,
        }}
      />
    </div>
  );
};

export default CollaborativeEditor;
