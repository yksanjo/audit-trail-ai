import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import AuditLogs from './pages/AuditLogs'
import DecisionLineage from './pages/DecisionLineage'
import Verification from './pages/Verification'
import Compliance from './pages/Compliance'
import Export from './pages/Export'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/audit-logs" element={<AuditLogs />} />
        <Route path="/lineage/:decisionId?" element={<DecisionLineage />} />
        <Route path="/verification" element={<Verification />} />
        <Route path="/compliance" element={<Compliance />} />
        <Route path="/export" element={<Export />} />
      </Routes>
    </Layout>
  )
}

export default App
