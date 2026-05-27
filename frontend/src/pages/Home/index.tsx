import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

const architectureItems = [
  {
    title: '页面入口',
    description: '只保留首页路由，后续业务页面统一从 routes 注册并按页面目录扩展。',
  },
  {
    title: 'UI 基础层',
    description: 'Base UI / shadcn 风格 primitives 作为唯一基础组件层，避免重复组件体系。',
  },
  {
    title: '工程边界',
    description: '布局、路由、服务层、样式 token 和测试入口分层保留，方便 AI 按规则增量开发。',
  },
];

export default function Home() {
  return (
    <section className="mx-auto flex min-h-[calc(100vh-7.5rem)] max-w-6xl flex-col justify-center px-6 py-16">
      <div className="max-w-3xl">
        <Badge variant="secondary">Production frontend foundation</Badge>
        <h1 className="mt-5 text-4xl font-semibold tracking-normal text-foreground sm:text-5xl">
          AI News Hub 前端架构骨架
        </h1>
        <p className="mt-5 max-w-2xl text-base leading-7 text-muted-foreground">
          当前阶段只保留主页与生产级工程边界。业务页面、认证、3D 动画和数据域将在后续重构中按规则重新接入。
        </p>
      </div>

      <div className="mt-10 grid gap-4 md:grid-cols-3">
        {architectureItems.map((item) => (
          <Card key={item.title}>
            <CardHeader>
              <CardTitle>{item.title}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm leading-6 text-muted-foreground">{item.description}</p>
            </CardContent>
          </Card>
        ))}
      </div>
    </section>
  );
}
