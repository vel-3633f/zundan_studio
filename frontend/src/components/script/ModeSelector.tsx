import { Laugh, Clock, Zap } from "lucide-react";
import { useNavigate } from "react-router-dom";

const ModeSelector = () => {
  const navigate = useNavigate();

  const handleSelectLong = () => {
    // 既存の長尺動画ページへ
    // 現在のページがすでに長尺動画ページなので何もしない
  };

  const handleSelectShort = () => {
    // ショート動画ページへ遷移
    navigate("/scripts/short");
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {/* 長尺動画カード */}
      <button
        onClick={handleSelectLong}
        className="p-6 rounded-lg border-2 border-primary-500 bg-primary-50 dark:bg-primary-900/20 hover:bg-primary-100 dark:hover:bg-primary-900/30 transition-colors text-left"
      >
        <div className="flex flex-col items-center gap-3">
          <Clock className="h-8 w-8 text-primary-600 dark:text-primary-400" />
          <div className="text-center">
            <h3 className="text-lg font-bold text-primary-900 dark:text-primary-100">
              😂 長尺動画（5-10分）
            </h3>
            <p className="text-sm mt-1 text-primary-700 dark:text-primary-300">
              詳細なストーリー展開
            </p>
            <div className="flex flex-wrap justify-center gap-2 mt-3">
              <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-primary-200 text-primary-800 dark:bg-primary-800 dark:text-primary-200">
                60-120セリフ
              </span>
              <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-primary-200 text-primary-800 dark:bg-primary-800 dark:text-primary-200">
                7-9セクション
              </span>
            </div>
          </div>
        </div>
      </button>

      {/* ショート動画カード */}
      <button
        onClick={handleSelectShort}
        className="p-6 rounded-lg border-2 border-yellow-500 bg-yellow-50 dark:bg-yellow-900/20 hover:bg-yellow-100 dark:hover:bg-yellow-900/30 transition-colors text-left"
      >
        <div className="flex flex-col items-center gap-3">
          <Zap className="h-8 w-8 text-yellow-600 dark:text-yellow-400" />
          <div className="text-center">
            <h3 className="text-lg font-bold text-yellow-900 dark:text-yellow-100">
              ⚡ ショート動画（60秒）
            </h3>
            <p className="text-sm mt-1 text-yellow-700 dark:text-yellow-300">
              テンポの速い展開
            </p>
            <div className="flex flex-wrap justify-center gap-2 mt-3">
              <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-yellow-200 text-yellow-800 dark:bg-yellow-800 dark:text-yellow-200">
                12-18セリフ
              </span>
              <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-yellow-200 text-yellow-800 dark:bg-yellow-800 dark:text-yellow-200">
                1-2セクション
              </span>
              <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-yellow-200 text-yellow-800 dark:bg-yellow-800 dark:text-yellow-200">
                高速生成
              </span>
            </div>
          </div>
        </div>
      </button>
    </div>
  );
};

export default ModeSelector;
