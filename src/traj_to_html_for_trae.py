#!/usr/bin/env python3
"""
Traj to HTML Converter

This script converts traj.json files (trajectory files) to HTML format for better visualization.
It handles various message types including user messages, assistant responses, and tool calls.
"""

import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Any, Optional


class TrajToHTMLConverter:
    """Converts traj.json files to HTML format."""
    
    def __init__(self):
        self.css_styles = """
        <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }
        .header .meta {
            margin-top: 10px;
            opacity: 0.9;
            font-size: 0.9em;
        }
        .conversation {
            padding: 20px;
        }
        .message {
            margin-bottom: 20px;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .message.user {
            background-color: #e3f2fd;
            border-left: 4px solid #2196f3;
        }
        .message.assistant {
            background-color: #f3e5f5;
            border-left: 4px solid #9c27b0;
        }
        .message.tool {
            background-color: #fff3e0;
            border-left: 4px solid #ff9800;
        }
        .message-header {
            padding: 12px 20px;
            font-weight: bold;
            color: white;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .message.user .message-header {
            background-color: #2196f3;
        }
        .message.assistant .message-header {
            background-color: #9c27b0;
        }
        .message.tool .message-header {
            background-color: #ff9800;
        }
        .message-content {
            padding: 20px;
            white-space: pre-wrap;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 0.9em;
            line-height: 1.5;
            max-height: 400px;
            overflow-y: auto;
        }
        .tool-call {
            background-color: #fafafa;
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            margin: 10px 0;
            padding: 15px;
        }
        .tool-call-header {
            font-weight: bold;
            color: #666;
            margin-bottom: 10px;
            font-size: 0.9em;
        }
        .tool-call-content {
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 4px;
            padding: 10px;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 0.85em;
            overflow-x: auto;
        }
        .agent-badge {
            background-color: rgba(255,255,255,0.2);
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: normal;
        }
        .timestamp {
            font-size: 0.8em;
            opacity: 0.8;
        }
        .stats {
            background-color: #f8f9fa;
            padding: 15px 20px;
            border-top: 1px solid #e9ecef;
            display: flex;
            justify-content: space-around;
            text-align: center;
        }
        .stat-item {
            flex: 1;
        }
        .stat-number {
            font-size: 1.5em;
            font-weight: bold;
            color: #667eea;
        }
        .stat-label {
            font-size: 0.9em;
            color: #666;
            margin-top: 5px;
        }
        .copy-button {
            background-color: #4caf50;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.8em;
            margin-left: 10px;
        }
        .copy-button:hover {
            background-color: #45a049;
        }
        .search-box {
            margin: 20px;
            text-align: center;
        }
        .search-input {
            width: 300px;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 16px;
        }
        .highlight {
            background-color: yellow;
            padding: 2px;
        }
        </style>
        """
        
        self.js_script = """
        <script>
        function copyToClipboard(text) {
            navigator.clipboard.writeText(text).then(function() {
                alert('Copied to clipboard!');
            }, function(err) {
                console.error('Could not copy text: ', err);
            });
        }
        
        function searchMessages() {
            const searchTerm = document.getElementById('searchInput').value.toLowerCase();
            const messages = document.querySelectorAll('.message');
            
            messages.forEach(message => {
                const content = message.querySelector('.message-content').textContent.toLowerCase();
                const toolCalls = message.querySelectorAll('.tool-call-content');
                
                let hasMatch = content.includes(searchTerm);
                
                toolCalls.forEach(toolCall => {
                    if (toolCall.textContent.toLowerCase().includes(searchTerm)) {
                        hasMatch = true;
                    }
                });
                
                if (hasMatch) {
                    message.style.display = 'block';
                    if (searchTerm) {
                        highlightText(message, searchTerm);
                    }
                } else {
                    message.style.display = 'none';
                }
            });
        }
        
        function highlightText(element, searchTerm) {
            const contentDiv = element.querySelector('.message-content');
            if (contentDiv) {
                const text = contentDiv.textContent;
                const highlightedText = text.replace(
                    new RegExp(searchTerm, 'gi'),
                    match => `<span class="highlight">${match}</span>`
                );
                contentDiv.innerHTML = highlightedText;
            }
        }
        
        function clearSearch() {
            document.getElementById('searchInput').value = '';
            const messages = document.querySelectorAll('.message');
            messages.forEach(message => {
                message.style.display = 'block';
                const contentDiv = message.querySelector('.message-content');
                if (contentDiv) {
                    contentDiv.innerHTML = contentDiv.textContent;
                }
            });
        }
        </script>
        """
    
    def convert_traj_to_html(self, traj_data: List[Dict[str, Any]], filename: str = "trajectory") -> str:
        """Convert trajectory data to HTML format."""
        
        # Count message types
        user_count = sum(1 for msg in traj_data if msg.get('role') == 'user')
        assistant_count = sum(1 for msg in traj_data if msg.get('role') == 'assistant')
        tool_count = sum(1 for msg in traj_data if msg.get('role') == 'tool')
        
        html_parts = [
            "<!DOCTYPE html>",
            "<html lang='en'>",
            "<head>",
            "    <meta charset='UTF-8'>",
            "    <meta name='viewport' content='width=device-width, initial-scale=1.0'>",
            f"    <title>{filename} - Trajectory Viewer</title>",
            self.css_styles,
            "</head>",
            "<body>",
            "    <div class='container'>",
            "        <div class='header'>",
            f"            <h1>{filename}</h1>",
            "            <div class='meta'>",
            f"                <div>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>",
            f"                <div>Total Messages: {len(traj_data)}</div>",
            "            </div>",
            "        </div>",
            "        <div class='search-box'>",
            "            <input type='text' id='searchInput' class='search-input' placeholder='Search messages...' onkeyup='searchMessages()'>",
            "            <button onclick='clearSearch()' class='copy-button'>Clear</button>",
            "        </div>",
            "        <div class='conversation'>"
        ]
        
        # Process each message
        for i, message in enumerate(traj_data):
            html_parts.append(self._format_message(message, i))
        
        html_parts.extend([
            "        </div>",
            "        <div class='stats'>",
            "            <div class='stat-item'>",
            f"                <div class='stat-number'>{user_count}</div>",
            "                <div class='stat-label'>User Messages</div>",
            "            </div>",
            "            <div class='stat-item'>",
            f"                <div class='stat-number'>{assistant_count}</div>",
            "                <div class='stat-label'>Assistant Messages</div>",
            "            </div>",
            "            <div class='stat-item'>",
            f"                <div class='stat-number'>{tool_count}</div>",
            "                <div class='stat-label'>Tool Responses</div>",
            "            </div>",
            "        </div>",
            "    </div>",
            self.js_script,
            "</body>",
            "</html>"
        ])
        
        return "\n".join(html_parts)
    
    def _format_message(self, message: Dict[str, Any], index: int) -> str:
        """Format a single message as HTML."""
        role = message.get('role', 'unknown')
        content = message.get('content', '')
        agent = message.get('agent', '')
        tool_calls = message.get('tool_calls', [])
        tool_call_id = message.get('tool_call_id', '')
        
        # Determine message class and header
        if role == 'user':
            message_class = 'user'
            header_text = '👤 User'
        elif role == 'assistant':
            message_class = 'assistant'
            header_text = '🤖 Assistant'
        elif role == 'tool':
            message_class = 'tool'
            header_text = '🔧 Tool Response'
        else:
            message_class = 'unknown'
            header_text = f'❓ {role.title()}'
        
        # Add agent info if available
        if agent:
            header_text += f" <span class='agent-badge'>{agent}</span>"
        
        # Add tool call ID if available
        if tool_call_id:
            header_text += f" <span class='agent-badge'>{tool_call_id}</span>"
        
        html_parts = [
            f"            <div class='message {message_class}'>",
            f"                <div class='message-header'>",
            f"                    {header_text}",
            f"                    <span class='timestamp'>Message #{index + 1}</span>",
            "                </div>",
            "                <div class='message-content'>"
        ]
        
        # Add content
        if content:
            html_parts.append(f"                    {self._escape_html(content)}")
        
        # Add tool calls if present
        if tool_calls:
            for tool_call in tool_calls:
                html_parts.append(self._format_tool_call(tool_call))
        
        html_parts.extend([
            "                </div>",
            "            </div>"
        ])
        
        return "\n".join(html_parts)
    
    def _format_tool_call(self, tool_call: Dict[str, Any]) -> str:
        """Format a tool call as HTML."""
        tool_type = tool_call.get('type', 'unknown')
        function_info = tool_call.get('function', {})
        function_name = function_info.get('name', 'unknown')
        arguments = function_info.get('arguments', '')
        tool_id = tool_call.get('id', '')
        
        html_parts = [
            "                    <div class='tool-call'>",
            "                        <div class='tool-call-header'>",
            f"                            🛠️ {tool_type.title()}: {function_name}",
            f"                            <button class='copy-button' onclick='copyToClipboard(`{self._escape_js(arguments)}`)'>Copy Args</button>",
            "                        </div>",
            "                        <div class='tool-call-content'>",
            f"                            <strong>Arguments:</strong><br>",
            f"                            {self._escape_html(arguments)}"
        ]
        
        if tool_id:
            html_parts.extend([
            f"                            <br><br><strong>Tool ID:</strong> {tool_id}"
            ])
        
        html_parts.extend([
            "                        </div>",
            "                    </div>"
        ])
        
        return "\n".join(html_parts)
    
    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters."""
        return (text.replace('&', '&amp;')
                   .replace('<', '&lt;')
                   .replace('>', '&gt;')
                   .replace('"', '&quot;')
                   .replace("'", '&#39;'))
    
    def _escape_js(self, text: str) -> str:
        """Escape JavaScript special characters."""
        return (text.replace('\\', '\\\\')
                   .replace('`', '\\`')
                   .replace('$', '\\$'))
    
    def save_html(self, html_content: str, output_path: str) -> None:
        """Save HTML content to a file."""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"HTML file saved to: {output_path}")


def main():
    """Main function to handle command line usage."""
    if len(sys.argv) < 2:
        print("Usage: python traj_to_html.py <traj_file.json> [output_file.html]")
        print("Example: python traj_to_html.py sample-trajs.json output.html")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else input_file.replace('.json', '.html')
    
    # Ensure output file has .html extension
    if not output_file.endswith('.html'):
        output_file += '.html'
    
    try:
        # Read and parse the JSON file
        with open(input_file, 'r', encoding='utf-8') as f:
            traj_data = json.load(f)
        
        # Convert to HTML
        converter = TrajToHTMLConverter()
        html_content = converter.convert_traj_to_html(traj_data, os.path.basename(input_file))
        
        # Save the HTML file
        converter.save_html(html_content, output_file)
        
        print(f"Successfully converted {input_file} to {output_file}")
        print(f"Open {output_file} in your web browser to view the trajectory")
        
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in file '{input_file}': {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
