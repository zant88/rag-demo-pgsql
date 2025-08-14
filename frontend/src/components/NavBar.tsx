import Link from 'next/link';
import { useRouter } from 'next/router';

const navItems = [
  { href: '/chat', label: 'Chat' },
  { href: '/upload', label: 'Document Upload' },
  { href: '/manual', label: 'Manual Input' },
];

export default function NavBar() {
  const router = useRouter();
  return (
    <nav className="w-full bg-white shadow mb-6">
      <div className="max-w-4xl mx-auto flex items-center justify-between p-4">
        <span className="text-xl font-bold text-blue-600">RAG Knowledge App</span>
        <div className="flex gap-6">
          {navItems.map((item) => (
            <Link key={item.href} href={item.href} legacyBehavior>
              <a
                className={`px-3 py-2 rounded hover:bg-blue-100 transition-colors ${
                  router.pathname === item.href ? 'bg-blue-500 text-white' : 'text-blue-700'
                }`}
              >
                {item.label}
              </a>
            </Link>
          ))}
        </div>
      </div>
    </nav>
  );
}
