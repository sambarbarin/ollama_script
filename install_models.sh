#!/bin/bash

# Script d'installation et de gestion des modèles Ollama
# Usage: ./install_models.sh [commande]

set -e

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction pour afficher les messages
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Vérifier si Ollama est installé
check_ollama() {
    if ! command -v ollama &> /dev/null; then
        print_error "Ollama n'est pas installé. Veuillez l'installer d'abord :"
        echo "sudo snap install ollama"
        echo "ou"
        echo "curl -fsSL https://ollama.com/install.sh | sh"
        exit 1
    fi
    print_success "Ollama est installé"
}

# Vérifier si le service Ollama fonctionne
check_ollama_service() {
    if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        print_warning "Le service Ollama ne semble pas fonctionner"
        print_info "Démarrage du service Ollama..."
        ollama serve &
        sleep 5
        
        if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
            print_error "Impossible de démarrer le service Ollama"
            exit 1
        fi
    fi
    print_success "Service Ollama opérationnel"
}

# Installer les modèles de base
install_basic_models() {
    print_info "Installation des modèles de base..."
    
    local models=(
        "llama3.1:8b:Modèle généraliste performant (4.7GB)"
        "mistral:7b:Excellent pour le français (4.1GB)"
        "phi3:3.8b:Compact et efficace (2.3GB)"
    )
    
    for model_info in "${models[@]}"; do
        IFS=':' read -r model size description <<< "$model_info"
        print_info "Installation de $model - $description"
        if ollama pull "$model:$size" 2>/dev/null; then
            print_success "$model installé avec succès"
        else
            print_error "Échec de l'installation de $model"
        fi
    done
}

# Installer les modèles avancés
install_advanced_models() {
    print_info "Installation des modèles avancés..."
    
    local models=(
        "llama3.1:70b:Modèle très performant (40GB) - Attention: très volumineux!"
        "mixtral:8x7b:Modèle Mistral avancé (26GB)"
        "codellama:7b:Spécialisé programmation (3.8GB)"
    )
    
    for model_info in "${models[@]}"; do
        IFS=':' read -r model size description <<< "$model_info"
        print_warning "$model - $description"
        read -p "Voulez-vous installer $model? (o/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[OoYy]$ ]]; then
            print_info "Installation de $model..."
            if ollama pull "$model:$size" 2>/dev/null; then
                print_success "$model installé avec succès"
            else
                print_error "Échec de l'installation de $model"
            fi
        fi
    done
}

# Installer les modèles multimodaux
install_multimodal_models() {
    print_info "Installation des modèles multimodaux (vision + texte)..."
    
    local models=(
        "llava:7b:Modèle vision + langage (4.7GB)"
        "bakllava:7b:Vision améliorée (4.7GB)"
    )
    
    for model_info in "${models[@]}"; do
        IFS=':' read -r model size description <<< "$model_info"
        print_info "Installation de $model - $description"
        if ollama pull "$model:$size" 2>/dev/null; then
            print_success "$model installé avec succès"
        else
            print_error "Échec de l'installation de $model"
        fi
    done
}

# Lister les modèles installés
list_models() {
    print_info "Modèles installés :"
    ollama list
}

# Afficher l'utilisation des ressources
show_status() {
    print_info "Statut des modèles en cours d'exécution :"
    ollama ps
}

# Nettoyer les modèles non utilisés
cleanup_models() {
    print_warning "Cette action supprimera les modèles sélectionnés"
    print_info "Modèles actuellement installés :"
    ollama list
    
    echo
    read -p "Entrez le nom du modèle à supprimer (ou 'all' pour tout supprimer): " model_name
    
    if [ "$model_name" = "all" ]; then
        read -p "Êtes-vous sûr de vouloir supprimer TOUS les modèles? (tapez 'oui'): " confirm
        if [ "$confirm" = "oui" ]; then
            ollama list | grep -v '^NAME' | awk '{print $1}' | xargs -I {} ollama rm {}
            print_success "Tous les modèles ont été supprimés"
        else
            print_info "Suppression annulée"
        fi
    elif [ -n "$model_name" ]; then
        if ollama rm "$model_name" 2>/dev/null; then
            print_success "Modèle $model_name supprimé"
        else
            print_error "Impossible de supprimer $model_name"
        fi
    fi
}

# Tester la connexion avec l'application
test_app_connection() {
    print_info "Test de connexion avec l'application Flask..."
    
    if curl -s http://localhost:5000/api/models > /dev/null 2>&1; then
        print_success "Application Flask accessible"
        print_info "Modèles détectés par l'application :"
        curl -s http://localhost:5000/api/models | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if data.get('success'):
        for model in data.get('models', []):
            print(f'  - {model}')
    else:
        print('  Erreur:', data.get('error', 'Inconnue'))
except:
    print('  Impossible de parser la réponse')
"
    else
        print_warning "Application Flask non accessible sur http://localhost:5000"
        print_info "Assurez-vous que l'application est démarrée avec : python3 app.py"
    fi
}

# Afficher l'aide
show_help() {
    echo "Script de gestion des modèles Ollama"
    echo
    echo "Usage: $0 [commande]"
    echo
    echo "Commandes disponibles :"
    echo "  install-basic      Installer les modèles de base (llama3.1, mistral, phi3)"
    echo "  install-advanced   Installer les modèles avancés (llama3.1:70b, mixtral, codellama)"
    echo "  install-multimodal Installer les modèles multimodaux (llava, bakllava)"
    echo "  install-all        Installer tous les modèles de base et multimodaux"
    echo "  list              Lister les modèles installés"
    echo "  status            Afficher le statut des modèles"
    echo "  cleanup           Supprimer des modèles"
    echo "  test              Tester la connexion avec l'application"
    echo "  check             Vérifier l'installation d'Ollama"
    echo "  help              Afficher cette aide"
    echo
}

# Menu principal
main() {
    print_info "🚀 Gestionnaire de modèles Ollama pour votre application"
    echo
    
    case "${1:-}" in
        "install-basic")
            check_ollama
            check_ollama_service
            install_basic_models
            list_models
            test_app_connection
            ;;
        "install-advanced")
            check_ollama
            check_ollama_service
            install_advanced_models
            list_models
            ;;
        "install-multimodal")
            check_ollama
            check_ollama_service
            install_multimodal_models
            list_models
            ;;
        "install-all")
            check_ollama
            check_ollama_service
            install_basic_models
            install_multimodal_models
            list_models
            test_app_connection
            ;;
        "list")
            check_ollama
            list_models
            ;;
        "status")
            check_ollama
            show_status
            ;;
        "cleanup")
            check_ollama
            cleanup_models
            ;;
        "test")
            check_ollama
            check_ollama_service
            test_app_connection
            ;;
        "check")
            check_ollama
            check_ollama_service
            print_success "Installation Ollama vérifiée avec succès"
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        "")
            show_help
            echo
            print_info "Pour commencer, utilisez : $0 install-basic"
            ;;
        *)
            print_error "Commande inconnue: $1"
            show_help
            exit 1
            ;;
    esac
}

# Exécuter le script
main "$@"