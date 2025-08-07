// Professional and modern emoji library for note titles
// Organized by categories with more sophisticated and business-appropriate emojis

export const professionalEmojis = {
  // Business & Work
  business: ['💼', '📊', '📈', '💹', '🎯', '🚀', '⚡', '🔥', '💡', '🏆', '🎖️', '🏅', '📌', '🔔', '💎'],
  
  // Technology & Development
  technology: ['💻', '🖥️', '📱', '⚙️', '🔧', '🛠️', '🔨', '⚗️', '🧪', '🔬', '🧬', '🤖', '🎮', '🕹️', '🖲️'],
  
  // Education & Learning
  education: ['📚', '📖', '📝', '✏️', '🖊️', '🖍️', '📐', '📏', '🎓', '🏫', '🔍', '🔎', '🔭', '🔬', '🗺️'],
  
  // Communication & Media
  communication: ['📧', '📨', '📬', '📮', '📢', '📣', '📡', '📻', '🎙️', '🎧', '📹', '📷', '📸', '🎬', '🎞️'],
  
  // Documents & Files
  documents: ['📄', '📃', '📑', '🗂️', '📂', '📁', '🗃️', '🗄️', '📋', '📊', '📈', '📉', '📜', '🗞️', '📰'],
  
  // Time & Planning
  time: ['⏰', '⏱️', '⏲️', '🕐', '📅', '🗓️', '📆', '🗓️', '⌛', '⏳', '🔄', '🔃', '🔁', '🔀', '⏭️'],
  
  // Finance & Money
  finance: ['💰', '💵', '💴', '💶', '💷', '💸', '💳', '🏦', '🏧', '💹', '📊', '📈', '📉', '🧾', '🏪'],
  
  // Health & Wellness
  health: ['🏥', '💊', '💉', '🩺', '🩹', '🧘', '🏃', '🚴', '🏋️', '⚕️', '🧠', '🫀', '🫁', '🦴', '🦷'],
  
  // Travel & Places
  travel: ['✈️', '🚀', '🛸', '🚁', '🚂', '🚇', '🚗', '🗺️', '🧭', '🏔️', '🏖️', '🏝️', '🌍', '🌎', '🌏'],
  
  // Nature & Environment
  nature: ['🌱', '🌿', '🍃', '🌾', '🌳', '🌲', '🌴', '🌵', '🌺', '🌻', '🌸', '💐', '🌷', '🌹', '🏵️'],
  
  // Food & Culinary
  food: ['🍽️', '🥘', '🍲', '🥗', '🍱', '🍜', '🍝', '🍕', '🥪', '🍔', '🌮', '🥙', '🧆', '🍳', '🥧'],
  
  // Art & Design
  art: ['🎨', '🖌️', '🖍️', '✏️', '📐', '📏', '🎭', '🎪', '🎬', '🎤', '🎧', '🎵', '🎶', '🎼', '🎹'],
  
  // Science & Research
  science: ['🔬', '🔭', '🧬', '🧪', '⚗️', '🧫', '🦠', '🔬', '🌡️', '🧲', '⚛️', '🔋', '🔌', '💡', '🔦'],
  
  // Security & Privacy
  security: ['🔒', '🔐', '🔑', '🗝️', '🛡️', '⚔️', '🔓', '🔏', '🔔', '🚨', '🚦', '🚥', '⚠️', '🚫', '🔴'],
  
  // Legal & Compliance
  legal: ['⚖️', '📜', '📋', '📝', '🏛️', '👨‍⚖️', '👩‍⚖️', '🔨', '📑', '📄', '📃', '🗃️', '📂', '📁', '🗂️'],
  
  // Marketing & Sales
  marketing: ['📢', '📣', '🎯', '💰', '🛍️', '🛒', '🏷️', '🎁', '📦', '📮', '📤', '📥', '📨', '📧', '💌'],
  
  // Sports & Fitness
  sports: ['⚽', '🏀', '🏈', '⚾', '🎾', '🏐', '🏓', '🏸', '🏑', '🏒', '🥊', '🥋', '⛳', '🏆', '🥇'],
  
  // Weather & Climate
  weather: ['☀️', '🌤️', '⛅', '🌥️', '☁️', '🌦️', '🌧️', '⛈️', '🌩️', '🌨️', '❄️', '☃️', '⛄', '🌬️', '💨'],
  
  // Abstract & Symbols
  abstract: ['♾️', '🔷', '🔶', '🔸', '🔹', '🔺', '🔻', '🔲', '🔳', '⚪', '⚫', '🔴', '🟠', '🟡', '🟢']
};

// Function to get a professional emoji based on content keywords
export function getProfessionalEmoji(content) {
  const contentLower = content.toLowerCase();
  
  // Keywords mapping to categories
  const keywordMap = {
    // Business
    'meeting': '💼', 'project': '📊', 'strategy': '🎯', 'goal': '🎯', 'growth': '📈', 
    'success': '🏆', 'achievement': '🏅', 'milestone': '🎖️', 'launch': '🚀', 'idea': '💡',
    
    // Technology
    'code': '💻', 'programming': '⚙️', 'development': '🔧', 'software': '🖥️', 'app': '📱',
    'ai': '🤖', 'robot': '🤖', 'game': '🎮', 'tech': '🔬', 'digital': '💻',
    
    // Education
    'study': '📚', 'learn': '📖', 'course': '🎓', 'education': '🏫', 'research': '🔍',
    'analysis': '📊', 'report': '📋', 'presentation': '📊', 'lecture': '🎓', 'tutorial': '📝',
    
    // Communication
    'email': '📧', 'message': '📨', 'call': '📞', 'video': '📹', 'broadcast': '📡',
    'podcast': '🎙️', 'audio': '🎧', 'media': '📻', 'news': '📰', 'blog': '📝',
    
    // Finance
    'budget': '💰', 'finance': '💹', 'investment': '📈', 'money': '💵', 'payment': '💳',
    'bank': '🏦', 'crypto': '💎', 'stock': '📊', 'trading': '📉', 'revenue': '💸',
    
    // Health
    'health': '🏥', 'medical': '⚕️', 'fitness': '🏃', 'workout': '🏋️', 'wellness': '🧘',
    'medicine': '💊', 'doctor': '🩺', 'hospital': '🏥', 'mental': '🧠', 'therapy': '🫀',
    
    // Travel
    'travel': '✈️', 'trip': '🗺️', 'vacation': '🏖️', 'journey': '🧭', 'flight': '✈️',
    'hotel': '🏨', 'destination': '📍', 'adventure': '🏔️', 'explore': '🌍', 'tour': '🚌',
    
    // Food
    'recipe': '🍽️', 'cooking': '👨‍🍳', 'food': '🥘', 'restaurant': '🍴', 'meal': '🍱',
    'breakfast': '🍳', 'lunch': '🥗', 'dinner': '🍲', 'diet': '🥗', 'nutrition': '🥙',
    
    // Art & Creative
    'design': '🎨', 'art': '🖌️', 'creative': '✨', 'music': '🎵', 'photo': '📷',
    'video': '🎬', 'film': '🎞️', 'theater': '🎭', 'dance': '💃', 'paint': '🎨',
    
    // Science
    'science': '🔬', 'experiment': '🧪', 'chemistry': '⚗️', 'physics': '⚛️', 'biology': '🧬',
    'astronomy': '🔭', 'math': '📐', 'engineering': '⚙️', 'innovation': '💡', 'discovery': '🔍',
    
    // Security
    'security': '🔒', 'password': '🔑', 'privacy': '🛡️', 'protection': '🔐', 'safe': '🔒',
    'encryption': '🔐', 'authentication': '🔑', 'firewall': '🛡️', 'backup': '💾', 'secure': '🔒',
    
    // Time & Planning
    'schedule': '📅', 'calendar': '🗓️', 'deadline': '⏰', 'timer': '⏱️', 'planning': '📋',
    'agenda': '📝', 'appointment': '📆', 'reminder': '🔔', 'task': '✅', 'todo': '📝'
  };
  
  // Check for keyword matches
  for (const [keyword, emoji] of Object.entries(keywordMap)) {
    if (contentLower.includes(keyword)) {
      return emoji;
    }
  }
  
  // If no specific match, return a random professional emoji from a curated list
  const defaultProfessionalEmojis = [
    '📌', '📎', '🔖', '📍', '🎯', '💡', '📊', '📈', '📋', '📝',
    '🔍', '💼', '📚', '🎓', '⚡', '🚀', '🔥', '💎', '🏆', '⭐'
  ];
  
  // Use a simple hash of the content to consistently select the same emoji for the same content
  let hash = 0;
  for (let i = 0; i < content.length; i++) {
    hash = ((hash << 5) - hash) + content.charCodeAt(i);
    hash = hash & hash; // Convert to 32-bit integer
  }
  
  return defaultProfessionalEmojis[Math.abs(hash) % defaultProfessionalEmojis.length];
}

// Function to get category-specific emojis
export function getEmojisByCategory(category) {
  return professionalEmojis[category] || [];
}

// Function to get all professional emojis
export function getAllProfessionalEmojis() {
  return Object.values(professionalEmojis).flat();
}