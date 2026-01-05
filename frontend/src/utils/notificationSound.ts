/**
 * 軽めの通知音を再生する
 * Web Audio APIを使用してシンプルなビープ音を生成
 */
export const playNotificationSound = (): void => {
  try {
    const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
    
    // オシレーターを作成（軽めの音色）
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();
    
    // 音色を設定（サイン波で柔らかい音）
    oscillator.type = 'sine';
    oscillator.frequency.value = 800; // 800Hz（軽めの高音）
    
    // 音量を設定（軽めに）
    gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.3);
    
    // 接続
    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);
    
    // 短いビープ音を再生（0.3秒）
    oscillator.start(audioContext.currentTime);
    oscillator.stop(audioContext.currentTime + 0.3);
  } catch (error) {
    // エラーが発生しても処理を続行（通知音はオプション機能）
    console.warn('通知音の再生に失敗しました:', error);
  }
};

