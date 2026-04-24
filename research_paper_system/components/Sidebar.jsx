import React, { useState } from "react";
import {
  Home,
  Search,
  Star,
  Users,
  BarChart3,
  Share2,
  FileText,
  Lightbulb,
  Puzzle,
  ChevronLeft,
  ChevronRight,
  Sparkles,
} from "lucide-react";

/* ---------------- Menu Data ---------------- */
const MENU_SECTIONS = [
  {
    header: "Main",
    items: [
      { id: "dashboard", label: "Dashboard", icon: Home },
      { id: "search", label: "Search", icon: Search },
      { id: "best-papers", label: "Best Papers", icon: Star },
    ],
  },
  {
    header: "Analytics",
    items: [
      { id: "top-authors", label: "Top Authors", icon: Users },
      { id: "rankings", label: "Rankings", icon: BarChart3 },
      { id: "citation-graph", label: "Citation Graph", icon: Share2 },
    ],
  },
  {
    header: "Content",
    items: [
      { id: "summaries", label: "Summaries", icon: FileText },
      { id: "ideas", label: "Ideas", icon: Lightbulb },
      { id: "problem-statements", label: "Problem Statements", icon: Puzzle },
    ],
  },
];

/* ---------------- Menu Item ---------------- */
function MenuItem({ item, active, collapsed, onClick }) {
  const Icon = item.icon;
  const isActive = active === item.id;

  return (
    <li className="relative group">
      <button
        onClick={() => onClick(item.id)}
        aria-label={item.label}
        aria-current={isActive ? "page" : undefined}
        className={[
          "relative flex items-center w-full rounded-xl",
          "transition-all duration-300 ease-in-out",
          collapsed ? "justify-center px-2 py-3" : "px-3 py-2.5 gap-3",
          isActive
            ? "bg-gradient-to-r from-indigo-500/30 via-violet-500/20 to-fuchsia-500/10 " +
              "text-white font-semibold " +
              "shadow-[0_0_10px_rgba(99,102,241,0.6)]"
            : "text-gray-400 hover:text-white hover:bg-white/5 hover:scale-[1.05]",
        ].join(" ")}
      >
        {/* Active left indicator bar */}
        {isActive && (
          <span
            aria-hidden="true"
            className="absolute left-0 top-1/2 -translate-y-1/2 h-7 w-1 rounded-r-full
                       bg-gradient-to-b from-indigo-400 via-violet-500 to-fuchsia-500
                       shadow-[0_0_10px_rgba(139,92,246,0.8)]"
          />
        )}

        {/* Icon */}
        <Icon
          size={collapsed ? 20 : 18}
          strokeWidth={1.75}
          className={[
            "flex-shrink-0 transition-all duration-300",
            isActive
              ? "text-violet-300 drop-shadow-[0_0_6px_rgba(167,139,250,0.8)]"
              : "text-gray-400 group-hover:text-white group-hover:scale-110",
          ].join(" ")}
        />

        {!collapsed && (
          <span className="text-sm tracking-wide truncate">{item.label}</span>
        )}
      </button>

      {/* Tooltip when collapsed */}
      {collapsed && (
        <span
          role="tooltip"
          className="pointer-events-none absolute left-full top-1/2 -translate-y-1/2 ml-3 z-50
                     whitespace-nowrap rounded-md bg-slate-900/95 backdrop-blur px-2.5 py-1.5
                     text-xs font-medium text-white shadow-lg ring-1 ring-white/10
                     opacity-0 group-hover:opacity-100 -translate-x-1 group-hover:translate-x-0
                     transition-all duration-200"
        >
          {item.label}
        </span>
      )}
    </li>
  );
}

/* ---------------- Section ---------------- */
function Section({ section, active, collapsed, onClick, showDivider }) {
  return (
    <div>
      {showDivider && (
        <div
          aria-hidden="true"
          className="mx-3 my-3 h-px bg-gradient-to-r from-transparent via-white/10 to-transparent"
        />
      )}
      {!collapsed ? (
        <p className="px-4 pt-2 pb-2 text-[10px] font-bold tracking-[0.2em] text-gray-500 uppercase">
          {section.header}
        </p>
      ) : (
        <div className="py-1" aria-hidden="true" />
      )}
      <ul className="space-y-1 px-2">
        {section.items.map((item) => (
          <MenuItem
            key={item.id}
            item={item}
            active={active}
            collapsed={collapsed}
            onClick={onClick}
          />
        ))}
      </ul>
    </div>
  );
}

/* ---------------- Sidebar ---------------- */
export default function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);
  const [active, setActive] = useState("dashboard");

  return (
    <aside
      aria-label="Main navigation"
      className={[
        "relative h-screen flex flex-col",
        "transition-all duration-300 ease-in-out",
        collapsed ? "w-20" : "w-[260px]",
        "bg-gradient-to-b from-[#0b0b1f] via-[#1a1340] to-[#2a1050]",
        "backdrop-blur-xl border-r border-white/10",
        "shadow-[4px_0_30px_rgba(0,0,0,0.35)]",
        "rounded-r-2xl",
      ].join(" ")}
    >
      {/* Ambient glow */}
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-0 rounded-r-2xl overflow-hidden"
      >
        <div className="absolute -top-24 -left-10 w-64 h-64 bg-violet-600/20 blur-3xl rounded-full" />
        <div className="absolute bottom-0 -right-10 w-64 h-64 bg-fuchsia-600/15 blur-3xl rounded-full" />
      </div>

      {/* Header — logo icon only */}
      <div
        className={[
          "relative flex items-center px-4 py-5",
          collapsed ? "justify-center" : "justify-between",
        ].join(" ")}
      >
        <div
          aria-hidden="true"
          className="flex items-center justify-center h-10 w-10 rounded-xl
                     bg-gradient-to-br from-indigo-500 via-violet-500 to-fuchsia-500
                     shadow-[0_0_20px_rgba(139,92,246,0.5)] ring-1 ring-white/15"
        >
          <Sparkles size={20} strokeWidth={2} className="text-white" />
        </div>

        {!collapsed && (
          <button
            onClick={() => setCollapsed(true)}
            aria-label="Collapse sidebar"
            className="flex items-center justify-center h-8 w-8 rounded-lg
                       text-gray-400 hover:text-white hover:bg-white/10
                       transition-all duration-200"
          >
            <ChevronLeft size={16} />
          </button>
        )}
      </div>

      {/* Header divider */}
      <div
        aria-hidden="true"
        className="mx-3 h-px bg-gradient-to-r from-transparent via-white/10 to-transparent"
      />

      {/* Navigation */}
      <nav
        aria-label="Sidebar navigation"
        className="relative flex-1 overflow-y-auto py-3"
      >
        {MENU_SECTIONS.map((section, idx) => (
          <Section
            key={section.header}
            section={section}
            active={active}
            collapsed={collapsed}
            onClick={setActive}
            showDivider={idx > 0}
          />
        ))}
      </nav>

      {/* Expand button when collapsed */}
      {collapsed && (
        <div className="relative p-3 flex justify-center">
          <button
            onClick={() => setCollapsed(false)}
            aria-label="Expand sidebar"
            className="flex items-center justify-center h-9 w-9 rounded-xl
                       bg-white/5 text-gray-300 hover:text-white hover:bg-white/10
                       ring-1 ring-white/10 transition-all duration-200"
          >
            <ChevronRight size={16} />
          </button>
        </div>
      )}

      {/* Footer accent bar */}
      <div
        aria-hidden="true"
        className="relative h-1 w-full bg-gradient-to-r from-indigo-500 via-violet-500 to-fuchsia-500 rounded-br-2xl"
      />
    </aside>
  );
}
