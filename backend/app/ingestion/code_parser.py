"""Parse and extract code structure"""
from pathlib import Path
from typing import List, Dict
import ast
import re

class CodeParser:
    """Extract code chunks with metadata"""
    
    SUPPORTED_EXTENSIONS = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.jsx': 'javascript',
        '.tsx': 'typescript',
    }
    
    @staticmethod
    def extract_python_chunks(file_path: str, content: str) -> List[Dict]:
        """Extract functions and classes from Python file"""
        chunks = []
        
        try:
            tree = ast.parse(content)
        except:
            return chunks
        
        lines = content.split('\n')
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                start_line = node.lineno
                end_line = node.end_lineno or node.lineno
                
                code_lines = lines[start_line-1:end_line]
                code = '\n'.join(code_lines)
                
                chunks.append({
                    'file_path': file_path,
                    'symbol_name': node.name,
                    'symbol_type': 'class' if isinstance(node, ast.ClassDef) else 'function',
                    'start_line': start_line,
                    'end_line': end_line,
                    'code': code,
                    'language': 'python',
                    'class_name': '',
                    'parent_symbol': '',
                    'imports': [],
                    'dependencies': [],
                })
        
        return chunks
    
    @staticmethod
    def extract_javascript_chunks(file_path: str, content: str, language: str = 'javascript') -> List[Dict]:
        """Extract functions from JavaScript/TypeScript"""
        chunks = []
        lines = content.split('\n')
        
        # Simple regex patterns
        patterns = [
            (r'^\s*(?:async\s+)?function\s+(\w+)', 'function'),
            (r'^\s*(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\(', 'function'),
            (r'^\s*class\s+(\w+)', 'class'),
        ]
        
        for i, line in enumerate(lines):
            for pattern, symbol_type in patterns:
                match = re.match(pattern, line)
                if match:
                    symbol_name = match.group(1)
                    # Extract function body (simplified - takes next 15 lines)
                    end_line = min(i + 15, len(lines))
                    code = '\n'.join(lines[i:end_line])
                    
                    chunks.append({
                        'file_path': file_path,
                        'symbol_name': symbol_name,
                        'symbol_type': symbol_type,
                        'start_line': i + 1,
                        'end_line': end_line,
                        'code': code,
                        'language': language,
                        'class_name': '',
                        'parent_symbol': '',
                        'imports': [],
                        'dependencies': [],
                    })
                    break
        
        return chunks
    
    @classmethod
    def parse_repository(cls, repo_path: str) -> List[Dict]:
        """Parse entire repository"""
        chunks = []
        
        for file_path in Path(repo_path).rglob('*'):
            if not file_path.is_file():
                continue
            
            ext = file_path.suffix
            if ext not in cls.SUPPORTED_EXTENSIONS:
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                language = cls.SUPPORTED_EXTENSIONS[ext]
                
                if ext == '.py':
                    chunks.extend(cls.extract_python_chunks(str(file_path), content))
                elif ext in ['.js', '.jsx', '.ts', '.tsx']:
                    chunks.extend(cls.extract_javascript_chunks(str(file_path), content, language))
            
            except Exception as e:
                print(f"Error parsing {file_path}: {e}")
        
        return chunks