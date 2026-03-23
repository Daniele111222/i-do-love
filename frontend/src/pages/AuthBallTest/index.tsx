/**
 * AuthBall 组件测试页面
 */
import { useState } from 'react';
import { AuthBall } from '@/components/AuthBall';

type BallState = 'default' | 'looking' | 'shy' | 'happy';

const states: { value: BallState; label: string; desc: string }[] = [
  { value: 'default', label: '默认', desc: '正常状态，球体呈淡紫色' },
  { value: 'looking', label: '注视', desc: '眼睛跟随鼠标移动' },
  { value: 'shy', label: '害羞', desc: '球体变成粉红色' },
  { value: 'happy', label: '开心', desc: '瞳孔变成绿色，嘴巴张大' },
];

export default function AuthBallTest() {
  const [currentState, setCurrentState] = useState<BallState>('default');
  const [size, setSize] = useState(1.5);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 py-12 px-4">
      <div className="max-w-4xl mx-auto">
        {/* 标题 */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-white mb-4">AuthBall 组件测试</h1>
          <p className="text-gray-400">3D 拟人化球体组件 - 呼吸动画、眼睛跟随、表情变化</p>
        </div>

        {/* 3D 球体展示 */}
        <div className="bg-gray-800/50 backdrop-blur rounded-2xl p-8 mb-8">
          <AuthBall 
            state={currentState} 
            size={size} 
            className="w-full h-[450px]" 
          />
        </div>

        {/* 控制面板 */}
        <div className="bg-gray-800/50 backdrop-blur rounded-2xl p-8">
          {/* 状态选择 */}
          <div className="mb-8">
            <h2 className="text-xl font-semibold text-white mb-4">选择状态</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {states.map((s) => (
                <button
                  key={s.value}
                  onClick={() => setCurrentState(s.value)}
                  className={`p-4 rounded-xl transition-all ${
                    currentState === s.value
                      ? 'bg-primary-600 text-white ring-2 ring-primary-400'
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
                >
                  <div className="font-medium">{s.label}</div>
                  <div className="text-xs mt-1 opacity-75">{s.desc}</div>
                </button>
              ))}
            </div>
          </div>

          {/* 大小调节 */}
          <div>
            <h2 className="text-xl font-semibold text-white mb-4">
              球体大小: {size.toFixed(1)}
            </h2>
            <input
              type="range"
              min="0.5"
              max="3"
              step="0.1"
              value={size}
              onChange={(e) => setSize(parseFloat(e.target.value))}
              className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-primary-600"
            />
            <div className="flex justify-between text-gray-400 text-sm mt-2">
              <span>0.5</span>
              <span>3.0</span>
            </div>
          </div>
        </div>

        {/* 功能说明 */}
        <div className="mt-8 bg-gray-800/50 backdrop-blur rounded-2xl p-8">
          <h2 className="text-xl font-semibold text-white mb-4">功能特性</h2>
          <ul className="space-y-3 text-gray-300">
            <li className="flex items-start gap-3">
              <span className="text-primary-400 mt-1">•</span>
              <span><strong>呼吸动画</strong> - 球体持续进行微微的缩放和上下浮动</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-primary-400 mt-1">•</span>
              <span><strong>眼睛跟随</strong> - 瞳孔会跟随鼠标位置移动，并有平滑插值</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-primary-400 mt-1">•</span>
              <span><strong>眨眼动画</strong> - 每约 3 秒会自动眨眼一次</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-primary-400 mt-1">•</span>
              <span><strong>状态变化</strong> - 不同状态会影响球体颜色、瞳孔颜色和嘴巴形状</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}
