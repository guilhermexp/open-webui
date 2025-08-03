// Configurable YouTube extension that can switch between automatic and manual modes
export { Youtube as YoutubeAuto } from './youtube';
export { YoutubeManual } from './youtube-manual';

// Export the manual version as default for now
export { YoutubeManual as default } from './youtube-manual';
export * from './youtube-manual';