// Walk With I - 4 Setup Integration
// This script integrates the character setup UI with SillyTavern

(function () {
  // Check if SillyTavern's API is available
  if (typeof window.SillyTavern === 'undefined') {
    console.error('SillyTavern API not found. Make sure this script runs in the SillyTavern environment.');
    return;
  }

  // Reference to SillyTavern's API
  const ST = window.SillyTavern;

  // Initialize the setup UI when the document is loaded
  document.addEventListener('DOMContentLoaded', function () {
    initSetupUI();
  });

  // Function to initialize the setup UI
  function initSetupUI() {
    // Create an iframe to load the setup UI
    const iframe = document.createElement('iframe');
    iframe.id = 'walk-with-i-4-setup-iframe';
    iframe.src = 'walk_with_I_4_setup.html';
    iframe.style.width = '100%';
    iframe.style.height = '90vh';
    iframe.style.border = 'none';

    // Create a modal to display the setup UI
    const modal = document.createElement('div');
    modal.id = 'walk-with-i-4-setup-modal';
    modal.style.position = 'fixed';
    modal.style.top = '0';
    modal.style.left = '0';
    modal.style.width = '100%';
    modal.style.height = '100%';
    modal.style.backgroundColor = 'rgba(0, 0, 0, 0.8)';
    modal.style.zIndex = '9999';
    modal.style.display = 'flex';
    modal.style.justifyContent = 'center';
    modal.style.alignItems = 'center';

    // Close button for the modal
    const closeButton = document.createElement('button');
    closeButton.textContent = '×';
    closeButton.style.position = 'absolute';
    closeButton.style.top = '10px';
    closeButton.style.right = '10px';
    closeButton.style.backgroundColor = '#8B0000';
    closeButton.style.color = 'white';
    closeButton.style.border = 'none';
    closeButton.style.borderRadius = '50%';
    closeButton.style.width = '40px';
    closeButton.style.height = '40px';
    closeButton.style.fontSize = '24px';
    closeButton.style.cursor = 'pointer';
    closeButton.style.zIndex = '10000';

    closeButton.addEventListener('click', function () {
      document.body.removeChild(modal);
    });

    // Append iframe and close button to modal
    modal.appendChild(iframe);
    modal.appendChild(closeButton);

    // Append modal to body
    document.body.appendChild(modal);

    // Set up message listener for communication from the iframe
    window.addEventListener('message', function (event) {
      // Check if the message is from our setup UI
      if (event.data && event.data.type === 'walk-with-i-4-setup') {
        handleSetupMessage(event.data);
      }
    });
  }

  // Handle messages from the setup UI
  function handleSetupMessage(data) {
    if (data.action === 'submit') {
      // Close the modal
      const modal = document.getElementById('walk-with-i-4-setup-modal');
      if (modal) {
        document.body.removeChild(modal);
      }

      // Send the setup data to the AI
      sendSetupToAI(data.setup);
    }
  }

  // Function to send setup data to SillyTavern's AI
  function sendSetupToAI(setup) {
    // Format the setup data as a message
    const message = `
## 角色设置
- 性别: ${setup.gender}
- 个人特质: ${setup.traits}
- 所属势力: ${setup.faction}

## 势力信息
- 契约从者: ${setup.servants.join(', ')}
- 所在位置: ${setup.location}
- 战舰特质: ${setup.warship}

## 开局事件
${setup.event}

请根据以上设置开始游戏。
`;

    // Send the message to the AI using SillyTavern's API
    ST.sendSystemMessage(message);
  }

  // Add a button to the SillyTavern UI to open the setup modal
  function addSetupButton() {
    // Create the button
    const button = document.createElement('button');
    button.id = 'walk-with-i-4-setup-button';
    button.textContent = 'Walk With I - 4 设置';
    button.className = 'menu_button';
    button.addEventListener('click', initSetupUI);

    // Find a suitable place to add the button
    const menuArea = document.querySelector('#rm_button_container');
    if (menuArea) {
      menuArea.appendChild(button);
    }
  }

  // Initialize the plugin
  function init() {
    console.log('Walk With I - 4 Setup initialized');
    addSetupButton();
  }

  // Initialize when the page is loaded
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
