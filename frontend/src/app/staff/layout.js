import Sidebar from "@/components/common/Sidebar";

export default function StaffLayout({ children }) {
  return (
    <div className="staff-layout">
      <Sidebar />
      <main className="staff-main">
        {children}
      </main>
    </div>
  );
}
