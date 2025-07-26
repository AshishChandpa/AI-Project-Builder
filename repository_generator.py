import requests
import json
import os
from pathlib import Path
import time


class CursorCloneClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api/v1"

    def generate_code(self, prompt, language="python", context="", provider="gemini"):
        """Generate code using the AI service"""
        url = f"{self.api_base}/ai/generate"
        payload = {
            "prompt": prompt,
            "language": language,
            "context": context,
            "provider": provider
        }

        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"API Error: {response.status_code} - {response.text}")

    def explain_code(self, code, language="python", provider="gemini"):
        """Get code explanation"""
        url = f"{self.api_base}/ai/explain"
        payload = {
            "prompt": code,
            "language": language,
            "provider": provider
        }

        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"API Error: {response.status_code} - {response.text}")

    def review_code(self, code, language="python", provider="gemini"):
        """Get code review"""
        url = f"{self.api_base}/ai/review"
        payload = {
            "prompt": code,
            "language": language,
            "provider": provider
        }

        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"API Error: {response.status_code} - {response.text}")


def generate_repository_structure(client, project_name, project_type):
    """Generate complete repository structure"""

    # Define repository templates
    templates = {
        "fastapi_backend": {
            "description": "FastAPI backend with authentication, database, and API endpoints",
            "files": {
                "main.py": "Create a FastAPI main application with CORS, authentication middleware, and health endpoints",
                "models/user.py": "Create SQLAlchemy User model with authentication fields",
                "models/post.py": "Create SQLAlchemy Post model with relationship to User",
                "routers/auth.py": "Create FastAPI router for user authentication (login, register, refresh token)",
                "routers/posts.py": "Create FastAPI router for CRUD operations on posts",
                "database.py": "Create database connection and session management with SQLAlchemy",
                "auth.py": "Create JWT authentication utilities and password hashing",
                "requirements.txt": "List all Python dependencies for FastAPI, SQLAlchemy, JWT, etc.",
                "Dockerfile": "Create Dockerfile for FastAPI application",
                "docker-compose.yml": "Create docker-compose with FastAPI app and PostgreSQL database",
                ".env.example": "Create example environment variables file",
                "README.md": "Create comprehensive README with setup instructions and API documentation"
            }
        },
        "react_frontend": {
            "description": "React frontend with routing, state management, and components",
            "files": {
                "src/App.js": "Create main React App component with routing using React Router",
                "src/components/Header.js": "Create responsive header component with navigation",
                "src/components/PostList.js": "Create component to display list of posts with pagination",
                "src/components/PostForm.js": "Create form component for creating/editing posts",
                "src/components/Login.js": "Create login form component with validation",
                "src/pages/Dashboard.js": "Create dashboard page with user statistics and quick actions",
                "src/services/api.js": "Create API service layer for backend communication",
                "src/context/AuthContext.js": "Create authentication context for state management",
                "src/hooks/useAuth.js": "Create custom hook for authentication logic",
                "package.json": "Create package.json with React, React Router, Axios dependencies",
                "Dockerfile": "Create Dockerfile for React application",
                "README.md": "Create README with setup instructions and component documentation"
            }
        },
        "python_cli": {
            "description": "Python CLI application with argument parsing and modular structure",
            "files": {
                "main.py": "Create main CLI entry point with argument parsing using argparse",
                "cli/commands/generate.py": "Create generate command for code generation",
                "cli/commands/analyze.py": "Create analyze command for code analysis",
                "core/generator.py": "Create core code generation logic",
                "core/analyzer.py": "Create core code analysis logic",
                "utils/file_handler.py": "Create file handling utilities",
                "utils/logger.py": "Create logging configuration and utilities",
                "config.py": "Create configuration management",
                "requirements.txt": "List Python dependencies",
                "setup.py": "Create setup.py for package installation",
                "README.md": "Create comprehensive README with usage examples"
            }
        }
    }

    if project_type not in templates:
        print(f"Unknown project type: {project_type}")
        print(f"Available types: {', '.join(templates.keys())}")
        return

    template = templates[project_type]
    project_dir = Path(project_name)
    project_dir.mkdir(exist_ok=True)

    print(f"🚀 Generating {project_type} project: {project_name}")
    print(f"📝 Description: {template['description']}")
    print(f"📁 Creating {len(template['files'])} files...\n")

    for file_path, prompt in template['files'].items():
        print(f"⏳ Generating {file_path}...")

        # Determine language from file extension
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'cpp',
            '.go': 'go',
            '.rs': 'rust',
            '.html': 'html',
            '.css': 'css',
            '.sql': 'sql',
            '.yml': 'yaml',
            '.yaml': 'yaml',
            '.json': 'json',
            '.md': 'markdown'
        }

        file_ext = Path(file_path).suffix
        language = language_map.get(file_ext, 'python')

        try:
            # Generate code
            response = client.generate_code(
                prompt=prompt,
                language=language,
                context=f"Creating {project_type} project named {project_name}. This file is part of a larger application structure.",
                provider="gemini"
            )

            if response['success']:
                # Create directory structure
                full_path = project_dir / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)

                # Write generated code to file
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(response['response'])

                print(f"✅ Generated {file_path} ({len(response['response'])} chars)")
            else:
                print(f"❌ Failed to generate {file_path}: {response.get('error_message', 'Unknown error')}")

            # Add small delay to avoid rate limiting
            time.sleep(0.5)

        except Exception as e:
            print(f"❌ Error generating {file_path}: {str(e)}")

    print(f"\n🎉 Project '{project_name}' generated successfully!")
    print(f"📍 Location: {project_dir.absolute()}")
    print(f"📖 Check the README.md file for setup instructions")


def main():
    client = CursorCloneClient()

    print("🤖 Cursor Clone Repository Generator")
    print("=====================================")

    # Check if service is running
    try:
        response = requests.get(f"{client.base_url}/health")
        if response.status_code == 200:
            print("✅ Cursor Clone service is running")
        else:
            print("❌ Cursor Clone service is not responding")
            return
    except Exception as e:
        print(f"❌ Cannot connect to Cursor Clone service: {e}")
        return

    # Get user input
    project_name = input("\n📁 Enter project name: ").strip()
    if not project_name:
        print("❌ Project name is required")
        return

    print("\n📋 Available project types:")
    print("1. fastapi_backend - FastAPI REST API with authentication")
    print("2. react_frontend - React frontend application")
    print("3. python_cli - Python CLI application")

    project_type = input("\n🔧 Enter project type (1-3): ").strip()

    type_map = {
        "1": "fastapi_backend",
        "2": "react_frontend",
        "3": "python_cli"
    }

    if project_type in type_map:
        generate_repository_structure(client, project_name, type_map[project_type])
    else:
        print("❌ Invalid project type selected")


if __name__ == "__main__":
    main()
