#!/usr/bin/env python3
"""
Script pour gérer les modèles Ollama via l'API REST
Utilisez ce script quand la commande 'ollama' n'est pas disponible
"""

import requests
import json
import sys
import time
from typing import List, Dict, Optional

class OllamaManager:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
    
    def is_available(self) -> bool:
        """Vérifier si l'API Ollama est disponible"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def list_models(self) -> List[Dict]:
        """Lister les modèles installés"""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                data = response.json()
                return data.get('models', [])
            return []
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des modèles: {e}")
            return []
    
    def pull_model(self, model_name: str) -> bool:
        """Télécharger un nouveau modèle"""
        print(f"🔄 Téléchargement du modèle {model_name}...")
        
        try:
            response = requests.post(
                f"{self.base_url}/api/pull",
                json={"name": model_name},
                stream=True,
                timeout=3600  # 1 heure de timeout pour les gros modèles
            )
            
            if response.status_code != 200:
                print(f"❌ Erreur HTTP {response.status_code}")
                return False
            
            # Suivre le progrès du téléchargement
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line)
                        
                        # Afficher le statut
                        if 'status' in data:
                            status = data['status']
                            if 'completed' in data and 'total' in data:
                                completed = data['completed']
                                total = data['total']
                                percent = (completed / total) * 100 if total > 0 else 0
                                print(f"\r{status}: {percent:.1f}%", end='', flush=True)
                            else:
                                print(f"\r{status}", end='', flush=True)
                        
                        # Vérifier si terminé
                        if data.get('done', False):
                            print(f"\n✅ Modèle {model_name} téléchargé avec succès!")
                            return True
                            
                    except json.JSONDecodeError:
                        continue
            
            return True
            
        except requests.exceptions.Timeout:
            print(f"\n❌ Timeout lors du téléchargement de {model_name}")
            return False
        except Exception as e:
            print(f"\n❌ Erreur lors du téléchargement: {e}")
            return False
    
    def delete_model(self, model_name: str) -> bool:
        """Supprimer un modèle"""
        try:
            response = requests.delete(
                f"{self.base_url}/api/delete",
                json={"name": model_name}
            )
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Erreur lors de la suppression: {e}")
            return False
    
    def show_model_info(self, model_name: str) -> Optional[Dict]:
        """Afficher les informations d'un modèle"""
        try:
            response = requests.post(
                f"{self.base_url}/api/show",
                json={"name": model_name}
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des infos: {e}")
            return None

def format_size(size_bytes: int) -> str:
    """Formater la taille en unités lisibles"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

def print_models(models: List[Dict]):
    """Afficher la liste des modèles de façon formatée"""
    if not models:
        print("📭 Aucun modèle installé")
        return
    
    print("📋 Modèles installés:")
    print("-" * 60)
    print(f"{'Nom':<25} {'Taille':<12} {'Modifié':<15}")
    print("-" * 60)
    
    for model in models:
        name = model.get('name', 'Inconnu')
        size = format_size(model.get('size', 0))
        modified = model.get('modified_at', 'Inconnu')[:10]  # Juste la date
        print(f"{name:<25} {size:<12} {modified:<15}")

def main():
    if len(sys.argv) < 2:
        print("""
🚀 Gestionnaire de modèles Ollama

Usage: python3 manage_ollama_models.py <commande> [arguments]

Commandes disponibles:
  list                    - Lister les modèles installés
  pull <model_name>       - Télécharger un nouveau modèle
  delete <model_name>     - Supprimer un modèle
  info <model_name>       - Afficher les informations d'un modèle
  test                    - Tester la connexion à l'API
  suggest                 - Suggérer des modèles populaires à installer

Exemples:
  python3 manage_ollama_models.py list
  python3 manage_ollama_models.py pull llama3.1
  python3 manage_ollama_models.py pull codellama:7b
  python3 manage_ollama_models.py delete mistral:latest
        """)
        return
    
    manager = OllamaManager()
    command = sys.argv[1]
    
    # Vérifier la connexion
    if not manager.is_available():
        print("❌ Impossible de se connecter à l'API Ollama")
        print("Assurez-vous que le service Ollama fonctionne sur http://localhost:11434")
        return
    
    if command == "list":
        models = manager.list_models()
        print_models(models)
        
    elif command == "pull":
        if len(sys.argv) < 3:
            print("❌ Veuillez spécifier un nom de modèle")
            print("Exemple: python3 manage_ollama_models.py pull llama3.1")
            return
        
        model_name = sys.argv[2]
        success = manager.pull_model(model_name)
        if success:
            print(f"\n🎉 Le modèle {model_name} est maintenant disponible dans votre application!")
        
    elif command == "delete":
        if len(sys.argv) < 3:
            print("❌ Veuillez spécifier un nom de modèle")
            return
        
        model_name = sys.argv[2]
        confirm = input(f"⚠️  Êtes-vous sûr de vouloir supprimer {model_name} ? (o/N): ")
        if confirm.lower() in ['o', 'oui', 'y', 'yes']:
            if manager.delete_model(model_name):
                print(f"✅ Modèle {model_name} supprimé")
            else:
                print(f"❌ Impossible de supprimer {model_name}")
        else:
            print("Suppression annulée")
    
    elif command == "info":
        if len(sys.argv) < 3:
            print("❌ Veuillez spécifier un nom de modèle")
            return
        
        model_name = sys.argv[2]
        info = manager.show_model_info(model_name)
        if info:
            print(f"📊 Informations pour {model_name}:")
            print(json.dumps(info, indent=2))
        else:
            print(f"❌ Impossible de récupérer les infos pour {model_name}")
    
    elif command == "test":
        print("🔍 Test de connexion à l'API Ollama...")
        models = manager.list_models()
        print(f"✅ Connexion OK - {len(models)} modèle(s) installé(s)")
        print_models(models)
        
        # Test avec l'application Flask
        try:
            response = requests.get("http://localhost:5000/api/models", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"\n✅ Application Flask OK - {len(data.get('models', []))} modèle(s) détecté(s)")
                else:
                    print(f"\n❌ Application Flask: {data.get('error', 'Erreur inconnue')}")
            else:
                print(f"\n❌ Application Flask: HTTP {response.status_code}")
        except:
            print("\n⚠️  Application Flask non accessible (http://localhost:5000)")
    
    elif command == "suggest":
        print("🎯 Modèles populaires recommandés:")
        print()
        
        suggestions = [
            ("llama3.1", "Modèle généraliste excellent, équilibré (~4.7GB)"),
            ("llama3.1:70b", "Version très performante mais lourde (~40GB)"),
            ("codellama", "Spécialisé pour la programmation (~3.8GB)"),
            ("phi3", "Compact et rapide de Microsoft (~2.3GB)"),
            ("mixtral", "Très performant de Mistral AI (~26GB)"),
            ("llava", "Modèle multimodal (vision + texte) (~4.7GB)"),
            ("gemma2", "Nouveau modèle de Google (~5.4GB)"),
            ("qwen2", "Excellent modèle chinois multilingue (~4.4GB)"),
        ]
        
        for model, description in suggestions:
            print(f"  {model:<15} - {description}")
        
        print("\nPour installer un modèle:")
        print("python3 manage_ollama_models.py pull <nom_du_modèle>")
        print("\nExemple: python3 manage_ollama_models.py pull llama3.1")
    
    else:
        print(f"❌ Commande inconnue: {command}")
        print("Utilisez 'python3 manage_ollama_models.py' pour voir l'aide")

if __name__ == "__main__":
    main()