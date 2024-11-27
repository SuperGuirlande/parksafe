class PasswordFieldManager {
    constructor(fieldId) {
        this.field = document.getElementById(fieldId);
        if (!this.field) return;
        
        this.setupField();
        this.setupCapsLockDetection();
    }

    setupField() {
        // Créer le conteneur wrapper si le champ existe
        const wrapper = document.createElement('div');
        wrapper.className = 'relative w-full';
        this.field.parentNode.insertBefore(wrapper, this.field);
        wrapper.appendChild(this.field);

        // Ajouter le bouton toggle avec un style plus visible
        const toggleButton = document.createElement('button');
        toggleButton.type = 'button';
        toggleButton.className = 'absolute right-3 top-1/2 -translate-y-1/2 z-20 cursor-pointer';
        toggleButton.style.cssText = `
            position: absolute;
            right: 10px;
            top: 50%;
            transform: translateY(-50%);
            z-index: 20;
            cursor: pointer;
            background: none;
            border: none;
            padding: 5px;
        `;
        toggleButton.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5 eye-open" style="width: 20px; height: 20px;">
                <path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z" />
                <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5 eye-closed hidden" style="width: 20px; height: 20px;">
                <path stroke-linecap="round" stroke-linejoin="round" d="M3.98 8.223A10.477 10.477 0 001.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.45 10.45 0 0112 4.5c4.756 0 8.773 3.162 10.065 7.498a10.523 10.523 0 01-4.293 5.774M6.228 6.228L3 3m3.228 3.228l3.65 3.65m7.894 7.894L21 21m-3.228-3.228l-3.65-3.65m0 0a3 3 0 10-4.243-4.243m4.242 4.242L9.88 9.88" />
            </svg>
        `;

        wrapper.appendChild(toggleButton);

        // Ajouter l'alerte Caps Lock
        const capsLockAlert = document.createElement('div');
        capsLockAlert.className = 'absolute -bottom-6 left-0 text-sm text-red-600 hidden caps-lock-alert';
        capsLockAlert.textContent = 'Touche Majuscule activée';
        wrapper.appendChild(capsLockAlert);

        // Gérer le clic sur le bouton avec debug
        toggleButton.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            console.log('Toggle button clicked'); // Debug
            const type = this.field.type === 'password' ? 'text' : 'password';
            this.field.type = type;
            console.log('New input type:', type); // Debug
            toggleButton.querySelector('.eye-open').classList.toggle('hidden');
            toggleButton.querySelector('.eye-closed').classList.toggle('hidden');
        });
    }

    setupCapsLockDetection() {
        const checkCapsLock = (e) => {
            const capsLockAlert = this.field.parentNode.querySelector('.caps-lock-alert');
            if (e.getModifierState && e.getModifierState('CapsLock')) {
                capsLockAlert.classList.remove('hidden');
            } else {
                capsLockAlert.classList.add('hidden');
            }
        };

        this.field.addEventListener('focus', (e) => {
            if (e.getModifierState && e.getModifierState('CapsLock')) {
                const capsLockAlert = this.field.parentNode.querySelector('.caps-lock-alert');
                capsLockAlert.classList.remove('hidden');
            }
        });

        this.field.addEventListener('keydown', checkCapsLock);
        this.field.addEventListener('keyup', checkCapsLock);
        
        this.field.addEventListener('blur', () => {
            const capsLockAlert = this.field.parentNode.querySelector('.caps-lock-alert');
            capsLockAlert.classList.add('hidden');
        });
    }
}

// Debug initialization
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM Content Loaded'); // Debug
    
    // Pour la page de login
    const loginField = document.getElementById('password-field');
    if (loginField) {
        console.log('Login field found'); // Debug
        new PasswordFieldManager('password-field');
    }
    
    // Pour la page d'inscription
    const registerField1 = document.getElementById('password-field1');
    const registerField2 = document.getElementById('password-field2');
    
    if (registerField1) {
        console.log('Register field 1 found'); // Debug
        new PasswordFieldManager('password-field1');
    }
    if (registerField2) {
        console.log('Register field 2 found'); // Debug
        new PasswordFieldManager('password-field2');
    }
});