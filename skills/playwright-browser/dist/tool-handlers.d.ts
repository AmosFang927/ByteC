import { PlaywrightBrowserSkill } from './index.js';
export declare function handleToolCall(browser: PlaywrightBrowserSkill, name: string, args: any): Promise<{
    success: boolean;
}>;
