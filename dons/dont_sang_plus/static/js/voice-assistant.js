/**
 * Assistant Vocal IA pour Don Sang Plus
 * Guide interactif pour utilisateurs (hôpitaux & donneurs)
 */

console.log('🤖 Voice Assistant: Fichier chargé');

class VoiceAssistant {
    constructor() {
        console.log('🤖 Voice Assistant: Constructor appelé');
        this.isActive = false;
        this.isListening = false;
        this.synthesis = window.speechSynthesis;
        this.recognition = null;
        this.currentPage = this.detectCurrentPage();
        this.userType = this.detectUserType();
        this.language = 'fr-FR';
        this.tutorialMode = false;
        this.currentStep = 0;
        
        this.init();
    }

    init() {
        // Initialiser la reconnaissance vocale
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.recognition = new SpeechRecognition();
            this.recognition.continuous = false;
            this.recognition.lang = this.language;
            this.recognition.interimResults = false;
            this.recognition.maxAlternatives = 1;
            
            this.recognition.onresult = (event) => this.handleSpeechResult(event);
            this.recognition.onerror = (event) => this.handleSpeechError(event);
            this.recognition.onend = () => {
                this.isListening = false;
                this.updateUI();
            };
        }
        
        // Créer l'interface utilisateur
        this.createUI();
        
        // Charger les préférences
        this.loadPreferences();
        
        // Message de bienvenue
        if (this.isActive) {
            setTimeout(() => this.greetUser(), 1000);
        }
    }

    detectCurrentPage() {
        const path = window.location.pathname;
        
        // Pages donneurs
        if (path.includes('donor-dashboard')) return 'donor-dashboard';
        if (path.includes('my-rewards')) return 'donor-rewards';
        if (path.includes('donor-history')) return 'donor-history';
        if (path.includes('donor-messages')) return 'donor-messages';
        if (path.includes('respond')) return 'donor-respond';
        
        // Pages hôpitaux
        if (path.includes('hospital-dashboard')) return 'hospital-dashboard';
        if (path.includes('hospital-history')) return 'hospital-history';
        if (path.includes('hospital-messages')) return 'hospital-messages';
        if (path.includes('create-blood-request')) return 'hospital-create-request';
        if (path.includes('manage-donor-rankings')) return 'hospital-rankings';
        
        // Pages communes
        if (path.includes('login')) return 'login';
        if (path.includes('register')) return 'register';
        if (path === '/' || path === '') return 'home';
        
        return 'unknown';
    }

    detectUserType() {
        const path = window.location.pathname;
        if (path.includes('donor')) return 'donor';
        if (path.includes('hospital')) return 'hospital';
        return 'guest';
    }

    createUI() {
        console.log('🤖 Voice Assistant: Création de l\'UI');
        const html = `
            <div id="voice-assistant" class="voice-assistant ${this.isActive ? 'active' : ''}">
                <!-- Bouton principal flottant -->
                <button id="va-toggle" class="va-toggle" title="Assistant Vocal">
                    <i class="fas fa-microphone"></i>
                    <span class="va-pulse"></span>
                </button>
                
                <!-- Panneau de contrôle -->
                <div id="va-panel" class="va-panel" style="display: none;">
                    <div class="va-header">
                        <div class="va-avatar">
                            <i class="fas fa-robot"></i>
                        </div>
                        <div class="va-title">
                            <h4>Assistant IA</h4>
                            <p id="va-status">Prêt à vous aider</p>
                        </div>
                        <button id="va-close" class="va-close-btn">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    
                    <div class="va-body">
                        <div id="va-transcript" class="va-transcript"></div>
                        
                        <div class="va-controls">
                            <button id="va-listen" class="va-btn va-btn-primary">
                                <i class="fas fa-microphone"></i>
                                <span>Parler</span>
                            </button>
                            <button id="va-tutorial" class="va-btn va-btn-secondary">
                                <i class="fas fa-graduation-cap"></i>
                                <span>Tutoriel</span>
                            </button>
                            <button id="va-help" class="va-btn va-btn-info">
                                <i class="fas fa-question-circle"></i>
                                <span>Aide</span>
                            </button>
                        </div>
                        
                        <div class="va-suggestions">
                            <p class="va-label">Vous pouvez dire :</p>
                            <div id="va-suggestions-list"></div>
                        </div>
                    </div>
                    
                    <div class="va-footer">
                        <label class="va-checkbox">
                            <input type="checkbox" id="va-auto-guide" ${this.isActive ? 'checked' : ''}>
                            <span>Guide automatique</span>
                        </label>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', html);
        console.log('🤖 Voice Assistant: UI insérée dans le DOM');
        console.log('🤖 Bouton toggle:', document.getElementById('va-toggle'));
        this.attachEventListeners();
        this.updateSuggestions();
    }

    attachEventListeners() {
        // Bouton principal : démarre/arrête l'écoute directement
        document.getElementById('va-toggle').addEventListener('click', () => this.toggleVoiceAssistant());
        
        // Les autres boutons dans le panneau (si on décide de le réafficher)
        if (document.getElementById('va-close')) {
            document.getElementById('va-close').addEventListener('click', () => this.togglePanel());
        }
        if (document.getElementById('va-listen')) {
            document.getElementById('va-listen').addEventListener('click', () => this.startListening());
        }
        if (document.getElementById('va-tutorial')) {
            document.getElementById('va-tutorial').addEventListener('click', () => this.startTutorial());
        }
        if (document.getElementById('va-help')) {
            document.getElementById('va-help').addEventListener('click', () => this.provideHelp());
        }
        if (document.getElementById('va-auto-guide')) {
            document.getElementById('va-auto-guide').addEventListener('change', (e) => {
                this.isActive = e.target.checked;
                this.savePreferences();
            });
        }
    }

    // Nouvelle fonction : toggle directement l'assistant vocal
    toggleVoiceAssistant() {
        if (this.isListening) {
            // Si en écoute, on arrête tout
            this.stopListening();
            this.isActive = false;
        } else {
            // Sinon, on démarre l'écoute
            this.isActive = true;
            this.speak("Je vous écoute, que puis-je faire pour vous ?");
            setTimeout(() => this.startListening(), 1500);
        }
        this.updateUI();
    }
    
    stopListening() {
        if (this.recognition && this.isListening) {
            this.recognition.stop();
            this.isListening = false;
            this.speak("Arrêt de l'assistant");
        }
    }

    togglePanel() {
        const panel = document.getElementById('va-panel');
        const isVisible = panel.style.display !== 'none';
        panel.style.display = isVisible ? 'none' : 'block';
        
        if (!isVisible && this.isActive) {
            this.speak("Je suis là pour vous aider. Que puis-je faire pour vous ?");
        }
    }

    speak(text, options = {}) {
        // Annuler toute lecture en cours
        this.synthesis.cancel();
        
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = this.language;
        utterance.rate = options.rate || 0.9;
        utterance.pitch = options.pitch || 1.0;
        utterance.volume = options.volume || 1.0;
        
        // Afficher dans le transcript
        this.addToTranscript('Assistant', text);
        
        utterance.onend = () => {
            if (options.callback) options.callback();
        };
        
        this.synthesis.speak(utterance);
    }

    startListening() {
        if (!this.recognition) {
            this.speak("Désolé, votre navigateur ne supporte pas la reconnaissance vocale.");
            return;
        }
        
        if (this.isListening) {
            this.recognition.stop();
            return;
        }
        
        this.isListening = true;
        this.updateUI();
        this.recognition.start();
        
        document.getElementById('va-status').textContent = "J'écoute...";
        this.addToTranscript('System', '🎤 En écoute...');
    }

    handleSpeechResult(event) {
        const transcript = event.results[0][0].transcript;
        const confidence = event.results[0][0].confidence;
        
        this.addToTranscript('Vous', transcript);
        this.processCommand(transcript);
    }

    handleSpeechError(event) {
        console.error('Erreur de reconnaissance vocale:', event.error);
        let message = "Désolé, je n'ai pas bien compris.";
        
        if (event.error === 'no-speech') {
            message = "Je n'ai rien entendu. Pouvez-vous répéter ?";
        } else if (event.error === 'not-allowed') {
            message = "Veuillez autoriser l'accès au microphone.";
        }
        
        this.speak(message);
        document.getElementById('va-status').textContent = message;
    }

    processCommand(command) {
        const cmd = command.toLowerCase();
        
        // Commandes de navigation
        if (cmd.includes('tableau de bord') || cmd.includes('dashboard') || cmd.includes('accueil')) {
            this.navigate('dashboard');
        }
        else if (cmd.includes('historique')) {
            this.navigate('history');
        }
        else if (cmd.includes('message')) {
            this.navigate('messages');
        }
        else if (cmd.includes('avantage') || cmd.includes('récompense')) {
            this.navigate('rewards');
        }
        else if (cmd.includes('profil')) {
            this.navigate('profile');
        }
        // Commandes d'action
        else if (cmd.includes('créer') && cmd.includes('demande')) {
            this.speak("Je vous guide pour créer une demande de sang.");
            this.navigate('create-request');
        }
        else if (cmd.includes('donner') || cmd.includes('faire un don')) {
            this.speak("Je vais vous montrer les demandes disponibles.");
            this.scrollToElement('.blood-requests-section');
        }
        // Commandes d'aide
        else if (cmd.includes('aide') || cmd.includes('help')) {
            this.provideHelp();
        }
        else if (cmd.includes('tutoriel') || cmd.includes('apprendre')) {
            this.startTutorial();
        }
        else if (cmd.includes('répéter') || cmd.includes('encore')) {
            this.repeatLastInstruction();
        }
        // Commande non reconnue
        else {
            this.speak("Je n'ai pas compris votre demande. Dites 'aide' pour voir ce que je peux faire.");
        }
        
        document.getElementById('va-status').textContent = "Prêt à vous aider";
    }

    navigate(destination) {
        const routes = {
            'dashboard': this.userType === 'donor' ? '/donations/donor-dashboard/' : '/donations/hospital-dashboard/',
            'history': this.userType === 'donor' ? '/donations/donor-history/' : '/donations/hospital-history/',
            'messages': this.userType === 'donor' ? '/donations/donor-messages/' : '/donations/hospital-messages/',
            'rewards': '/donations/my-rewards/',
            'profile': '/donations/edit-profile/',
            'create-request': '/donations/create-blood-request/',
        };
        
        if (routes[destination]) {
            this.speak(`Je vous emmène vers ${destination}`);
            setTimeout(() => {
                window.location.href = routes[destination];
            }, 1000);
        }
    }

    greetUser() {
        const hour = new Date().getHours();
        let greeting = hour < 12 ? 'Bonjour' : hour < 18 ? 'Bon après-midi' : 'Bonsoir';
        
        const messages = {
            'donor': {
                'donor-dashboard': `${greeting} ! Bienvenue sur votre tableau de bord. Voulez-vous voir les demandes de sang disponibles ?`,
                'donor-rewards': `${greeting} ! Voici vos avantages et récompenses. Vous pouvez télécharger vos certificats en cliquant sur les boutons.`,
                'donor-history': `${greeting} ! Voici l'historique de vos dons. Vous pouvez voir tous vos dons complétés.`,
            },
            'hospital': {
                'hospital-dashboard': `${greeting} ! Bienvenue sur votre tableau de bord. Voulez-vous créer une nouvelle demande de sang ?`,
                'hospital-rankings': `${greeting} ! Voici le classement de vos donneurs. Vous pouvez créer des bons de réduction pour les récompenser.`,
            }
        };
        
        const message = messages[this.userType]?.[this.currentPage] || 
                       `${greeting} ! Je suis votre assistant vocal. Dites "aide" pour découvrir ce que je peux faire pour vous.`;
        
        this.speak(message);
    }

    startTutorial() {
        this.tutorialMode = true;
        this.currentStep = 0;
        
        const tutorials = {
            'donor': [
                "Bienvenue dans le tutoriel pour les donneurs ! Je vais vous guider étape par étape.",
                "Première étape : Votre tableau de bord. C'est ici que vous voyez toutes les informations importantes.",
                "Vous pouvez voir les demandes de sang urgentes en haut. Cliquez sur 'Je veux donner' pour répondre.",
                "Dans le menu à gauche, vous avez accès à vos messages, votre historique et vos avantages.",
                "Pour voir vos récompenses, cliquez sur 'Mes Avantages'. Plus vous donnez, plus vous obtenez de réductions !",
                "Tutoriel terminé ! Dites 'aide' si vous avez besoin de plus d'informations."
            ],
            'hospital': [
                "Bienvenue dans le tutoriel pour les hôpitaux ! Je vais vous guider étape par étape.",
                "Première étape : Votre tableau de bord. C'est ici que vous gérez vos demandes de sang.",
                "Pour créer une nouvelle demande, cliquez sur 'Nouvelle Demande'. Remplissez le formulaire avec les détails.",
                "Dans 'Historique', vous pouvez voir toutes vos demandes et changer leur statut.",
                "Quand un donneur a fait le don, changez le statut en 'Effectué' pour le système le comptabilise.",
                "Dans 'Classements Donneurs', vous pouvez voir vos donneurs fidèles et créer des bons de réduction.",
                "Tutoriel terminé ! Dites 'aide' si vous avez besoin de plus d'informations."
            ]
        };
        
        this.runTutorial(tutorials[this.userType] || tutorials['donor']);
    }

    runTutorial(steps) {
        if (this.currentStep >= steps.length) {
            this.tutorialMode = false;
            return;
        }
        
        this.speak(steps[this.currentStep], {
            callback: () => {
                this.currentStep++;
                if (this.currentStep < steps.length) {
                    setTimeout(() => this.runTutorial(steps), 2000);
                } else {
                    this.tutorialMode = false;
                }
            }
        });
    }

    provideHelp() {
        const helpMessages = {
            'donor': {
                'general': "Je peux vous aider à naviguer, voir les demandes de sang, consulter votre historique, et bien plus. Dites par exemple : 'montre moi les demandes', 'voir mon historique', ou 'mes avantages'.",
                'donor-dashboard': "Sur cette page, vous pouvez voir les demandes de sang urgentes, votre disponibilité, et vos messages. Cliquez sur 'Je veux donner' pour répondre à une demande.",
                'donor-rewards': "Ici, vous voyez tous vos avantages ! Plus vous donnez, plus vous montez de niveau. Vous pouvez télécharger vos certificats en PDF.",
            },
            'hospital': {
                'general': "Je peux vous aider à créer des demandes de sang, gérer vos réponses, et suivre vos donneurs. Dites par exemple : 'créer une demande', 'voir l'historique', ou 'classement des donneurs'.",
                'hospital-dashboard': "Sur cette page, vous pouvez voir vos demandes actives et créer de nouvelles demandes. Cliquez sur 'Nouvelle Demande' pour commencer.",
                'hospital-rankings': "Ici, vous pouvez voir tous vos donneurs fidèles, leur niveau, et créer des bons de réduction pour les récompenser.",
            }
        };
        
        const message = helpMessages[this.userType]?.[this.currentPage] || 
                       helpMessages[this.userType]?.['general'] || 
                       "Dites 'tutoriel' pour apprendre à utiliser l'application, ou posez-moi des questions spécifiques.";
        
        this.speak(message);
    }

    updateSuggestions() {
        const suggestions = {
            'donor-dashboard': ['Voir les demandes', 'Mon historique', 'Mes avantages', 'Mes messages'],
            'donor-rewards': ['Télécharger certificat', 'Voir mes points', 'Retour dashboard'],
            'hospital-dashboard': ['Créer une demande', 'Voir historique', 'Mes messages'],
            'hospital-rankings': ['Créer un bon', 'Voir profil donneur', 'Retour dashboard'],
        };
        
        const list = suggestions[this.currentPage] || ['Aide', 'Tutoriel', 'Navigation'];
        const html = list.map(s => `<button class="va-suggestion-btn">${s}</button>`).join('');
        
        document.getElementById('va-suggestions-list').innerHTML = html;
        
        // Ajouter les événements
        document.querySelectorAll('.va-suggestion-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                this.processCommand(btn.textContent);
            });
        });
    }

    addToTranscript(speaker, text) {
        const transcript = document.getElementById('va-transcript');
        const entry = document.createElement('div');
        entry.className = `va-message va-message-${speaker.toLowerCase()}`;
        entry.innerHTML = `<strong>${speaker}:</strong> ${text}`;
        transcript.appendChild(entry);
        transcript.scrollTop = transcript.scrollHeight;
    }

    scrollToElement(selector) {
        const element = document.querySelector(selector);
        if (element) {
            element.scrollIntoView({ behavior: 'smooth', block: 'center' });
            element.classList.add('va-highlight');
            setTimeout(() => element.classList.remove('va-highlight'), 2000);
        }
    }

    updateUI() {
        // Mettre à jour le bouton principal
        const toggleBtn = document.getElementById('va-toggle');
        const assistant = document.getElementById('voice-assistant');
        
        if (this.isListening) {
            toggleBtn.classList.add('listening');
            assistant.classList.add('active');
            toggleBtn.innerHTML = '<i class="fas fa-stop"></i>';
        } else {
            toggleBtn.classList.remove('listening');
            assistant.classList.remove('active');
            toggleBtn.innerHTML = '<i class="fas fa-microphone"></i>';
        }
        
        // Mettre à jour le bouton dans le panneau (si existe)
        const listenBtn = document.getElementById('va-listen');
        if (listenBtn) {
            if (this.isListening) {
                listenBtn.classList.add('listening');
                listenBtn.innerHTML = '<i class="fas fa-stop"></i><span>Arrêter</span>';
            } else {
                listenBtn.classList.remove('listening');
                listenBtn.innerHTML = '<i class="fas fa-microphone"></i><span>Parler</span>';
            }
        }
    }

    savePreferences() {
        localStorage.setItem('va-active', this.isActive);
    }

    loadPreferences() {
        const saved = localStorage.getItem('va-active');
        this.isActive = saved === 'true' || saved === null; // Actif par défaut
    }

    repeatLastInstruction() {
        // Répéter la dernière instruction selon la page
        this.greetUser();
    }
}

// Initialiser l'assistant au chargement de la page
console.log('🤖 Voice Assistant: Attente du DOMContentLoaded');
document.addEventListener('DOMContentLoaded', () => {
    console.log('🤖 Voice Assistant: DOM chargé, création de l\'assistant');
    try {
        window.voiceAssistant = new VoiceAssistant();
        console.log('🤖 Voice Assistant: Instance créée avec succès');
    } catch (error) {
        console.error('❌ Voice Assistant: Erreur lors de la création:', error);
    }
});
