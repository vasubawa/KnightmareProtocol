import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs/promises';
import path from 'path';

const SESSIONS_DIR = path.join(process.cwd(), 'data', 'sessions');

// Ensure sessions directory exists
async function ensureSessionsDir() {
  try {
    await fs.access(SESSIONS_DIR);
  } catch {
    await fs.mkdir(SESSIONS_DIR, { recursive: true });
  }
}

// GET - List all sessions
export async function GET() {
  try {
    await ensureSessionsDir();
    const files = await fs.readdir(SESSIONS_DIR);
    const sessions = await Promise.all(
      files
        .filter(f => f.endsWith('.json'))
        .map(async (file) => {
          const content = await fs.readFile(path.join(SESSIONS_DIR, file), 'utf-8');
          return JSON.parse(content);
        })
    );
    
    // Sort by timestamp (newest first)
    sessions.sort((a, b) => b.timestamp - a.timestamp);
    
    return NextResponse.json(sessions);
  } catch (error) {
    console.error('Error reading sessions:', error);
    return NextResponse.json({ error: 'Failed to read sessions' }, { status: 500 });
  }
}

// POST - Create new session
export async function POST(request: NextRequest) {
  try {
    await ensureSessionsDir();
    const session = await request.json();
    
    const filePath = path.join(SESSIONS_DIR, `${session.id}.json`);
    await fs.writeFile(filePath, JSON.stringify(session, null, 2));
    
    return NextResponse.json(session);
  } catch (error) {
    console.error('Error creating session:', error);
    return NextResponse.json({ error: 'Failed to create session' }, { status: 500 });
  }
}
