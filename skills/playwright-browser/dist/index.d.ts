export declare class PlaywrightBrowserSkill {
    private browser;
    private context;
    private page;
    private pages;
    private dialogHandler;
    private requestLogs;
    private responseLogs;
    private consoleLogs;
    private eventListeners;
    launch(options?: {
        browserType?: 'chromium' | 'firefox' | 'webkit';
        headless?: boolean;
        viewport?: {
            width: number;
            height: number;
        };
        userAgent?: string;
        locale?: string;
        timezone?: string;
        permissions?: string[];
        geolocation?: {
            latitude: number;
            longitude: number;
        };
        proxy?: {
            server: string;
            username?: string;
            password?: string;
        };
        deviceName?: string;
        recordVideo?: boolean;
        recordTrace?: boolean;
        slowMo?: number;
        args?: string[];
    }): Promise<{
        success: boolean;
        message: string;
    }>;
    close(): Promise<{
        success: boolean;
        message: string;
    }>;
    newPage(): Promise<{
        success: boolean;
        message: string;
        pageIndex: number;
    }>;
    switchPage(index: number): Promise<{
        success: boolean;
        message: string;
    }>;
    closePage(index?: number): Promise<{
        success: boolean;
        message: string;
    }>;
    getAllPages(): Promise<{
        success: boolean;
        pages: {
            index: number;
            url: string;
            title: Promise<string>;
        }[];
    }>;
    goto(url: string, options?: {
        waitUntil?: 'load' | 'domcontentloaded' | 'networkidle';
        timeout?: number;
    }): Promise<{
        success: boolean;
        url: string;
    }>;
    goBack(): Promise<{
        success: boolean;
        url: string;
    }>;
    goForward(): Promise<{
        success: boolean;
        url: string;
    }>;
    reload(): Promise<{
        success: boolean;
        url: string;
    }>;
    click(selector: string, options?: {
        timeout?: number;
        button?: 'left' | 'right' | 'middle';
        clickCount?: number;
    }): Promise<{
        success: boolean;
        selector: string;
    }>;
    dblclick(selector: string): Promise<{
        success: boolean;
        selector: string;
    }>;
    hover(selector: string): Promise<{
        success: boolean;
        selector: string;
    }>;
    fill(selector: string, value: string): Promise<{
        success: boolean;
        selector: string;
        value: string;
    }>;
    type(selector: string, text: string, options?: {
        delay?: number;
    }): Promise<{
        success: boolean;
        selector: string;
        text: string;
    }>;
    press(selector: string, key: string): Promise<{
        success: boolean;
        selector: string;
        key: string;
    }>;
    select(selector: string, value: string | string[]): Promise<{
        success: boolean;
        selector: string;
        value: string | string[];
    }>;
    check(selector: string): Promise<{
        success: boolean;
        selector: string;
    }>;
    uncheck(selector: string): Promise<{
        success: boolean;
        selector: string;
    }>;
    focus(selector: string): Promise<{
        success: boolean;
        selector: string;
    }>;
    drag(sourceSelector: string, targetSelector: string): Promise<{
        success: boolean;
        source: string;
        target: string;
    }>;
    getText(selector: string): Promise<{
        success: boolean;
        text: string | null;
    }>;
    getTitle(): Promise<{
        success: boolean;
        title: string;
    }>;
    getHTML(): Promise<{
        success: boolean;
        html: string;
    }>;
    getLinks(): Promise<{
        success: boolean;
        links: {
            text: any;
            href: any;
        }[];
    }>;
    getAttribute(selector: string, attribute: string): Promise<{
        success: boolean;
        attribute: string;
        value: string | null;
    }>;
    getInputValue(selector: string): Promise<{
        success: boolean;
        value: string;
    }>;
    isVisible(selector: string): Promise<{
        success: boolean;
        visible: boolean;
    }>;
    isEnabled(selector: string): Promise<{
        success: boolean;
        enabled: boolean;
    }>;
    isChecked(selector: string): Promise<{
        success: boolean;
        checked: boolean;
    }>;
    count(selector: string): Promise<{
        success: boolean;
        count: number;
    }>;
    waitForSelector(selector: string, options?: {
        timeout?: number;
        state?: 'attached' | 'detached' | 'visible' | 'hidden';
    }): Promise<{
        success: boolean;
        selector: string;
    }>;
    waitForNavigation(options?: {
        timeout?: number;
        waitUntil?: 'load' | 'domcontentloaded' | 'networkidle';
    }): Promise<{
        success: boolean;
        url: string;
    }>;
    waitForTimeout(timeout: number): Promise<{
        success: boolean;
        timeout: number;
    }>;
    waitForURL(url: string | RegExp, options?: {
        timeout?: number;
    }): Promise<{
        success: boolean;
        url: string;
    }>;
    screenshot(options?: {
        path?: string;
        fullPage?: boolean;
        type?: 'png' | 'jpeg';
        quality?: number;
    }): Promise<{
        success: boolean;
        screenshot: string;
    }>;
    screenshotElement(selector: string, options?: {
        path?: string;
    }): Promise<{
        success: boolean;
        screenshot: string;
    }>;
    pdf(options?: {
        path?: string;
        format?: string;
        printBackground?: boolean;
    }): Promise<{
        success: boolean;
        pdf: string;
    }>;
    evaluate(script: string, arg?: any): Promise<{
        success: boolean;
        result: unknown;
    }>;
    evaluateHandle(script: string): Promise<{
        success: boolean;
        handle: string;
    }>;
    addScriptTag(options: {
        url?: string;
        content?: string;
        type?: string;
    }): Promise<{
        success: boolean;
        message: string;
    }>;
    addStyleTag(options: {
        url?: string;
        content?: string;
    }): Promise<{
        success: boolean;
        message: string;
    }>;
    setCookies(cookies: Array<{
        name: string;
        value: string;
        domain?: string;
        path?: string;
        expires?: number;
        httpOnly?: boolean;
        secure?: boolean;
        sameSite?: 'Strict' | 'Lax' | 'None';
    }>): Promise<{
        success: boolean;
        message: string;
    }>;
    getCookies(): Promise<{
        success: boolean;
        cookies: import("playwright-core").Cookie[];
    }>;
    clearCookies(): Promise<{
        success: boolean;
        message: string;
    }>;
    setLocalStorage(key: string, value: string): Promise<{
        success: boolean;
        key: string;
        value: string;
    }>;
    getLocalStorage(key?: string): Promise<{
        success: boolean;
        result: string | null;
    }>;
    clearLocalStorage(): Promise<{
        success: boolean;
        message: string;
    }>;
    setExtraHTTPHeaders(headers: Record<string, string>): Promise<{
        success: boolean;
        message: string;
    }>;
    setOffline(offline: boolean): Promise<{
        success: boolean;
        offline: boolean;
    }>;
    route(url: string | RegExp, handler: 'abort' | 'continue' | 'fulfill'): Promise<{
        success: boolean;
        message: string;
    }>;
    handleDialog(action: 'accept' | 'dismiss', promptText?: string): Promise<{
        success: boolean;
        message: string;
    }>;
    uploadFile(selector: string, filePath: string | string[]): Promise<{
        success: boolean;
        selector: string;
        filePath: string | string[];
    }>;
    downloadFile(triggerSelector: string): Promise<{
        success: boolean;
        path: string;
        filename: string;
    }>;
    switchToFrame(selector: string): Promise<{
        success: boolean;
        message: string;
    }>;
    getFrames(): Promise<{
        success: boolean;
        frames: {
            name: string;
            url: string;
        }[];
    }>;
    setViewportSize(width: number, height: number): Promise<{
        success: boolean;
        width: number;
        height: number;
    }>;
    emulateMedia(options: {
        colorScheme?: 'light' | 'dark' | 'no-preference';
        media?: 'screen' | 'print';
    }): Promise<{
        success: boolean;
        options: {
            colorScheme?: "light" | "dark" | "no-preference";
            media?: "screen" | "print";
        };
    }>;
    getCurrentURL(): Promise<{
        success: boolean;
        url: string;
    }>;
    getViewportSize(): Promise<{
        success: boolean;
        viewport: {
            width: number;
            height: number;
        } | null;
    }>;
    scrollTo(x: number, y: number): Promise<{
        success: boolean;
        x: number;
        y: number;
    }>;
    scrollIntoView(selector: string): Promise<{
        success: boolean;
        selector: string;
    }>;
    private setupEventListeners;
    private setupPageEventListeners;
    getConsoleLogs(limit?: number): Promise<{
        success: boolean;
        logs: {
            type: string;
            text: string;
            timestamp: number;
        }[];
    }>;
    getRequestLogs(limit?: number): Promise<{
        success: boolean;
        logs: {
            url: string;
            method: string;
            timestamp: number;
        }[];
    }>;
    getResponseLogs(limit?: number): Promise<{
        success: boolean;
        logs: {
            url: string;
            status: number;
            timestamp: number;
        }[];
    }>;
    clearLogs(): Promise<{
        success: boolean;
        message: string;
    }>;
    waitForRequest(urlPattern: string | RegExp, timeout?: number): Promise<{
        success: boolean;
        url: string;
        method: string;
        headers: {
            [key: string]: string;
        };
    }>;
    waitForResponse(urlPattern: string | RegExp, timeout?: number): Promise<{
        success: boolean;
        url: string;
        status: number;
        headers: {
            [key: string]: string;
        };
    }>;
    waitForEvent(eventName: string, timeout?: number): Promise<{
        success: boolean;
        event: string;
    }>;
    blockRequests(patterns: string[]): Promise<{
        success: boolean;
        message: string;
        patterns: string[];
    }>;
    mockResponse(urlPattern: string | RegExp, response: {
        status?: number;
        body?: string;
        contentType?: string;
    }): Promise<{
        success: boolean;
        message: string;
    }>;
    unroute(urlPattern?: string | RegExp): Promise<{
        success: boolean;
        message: string;
    }>;
    setRequestInterception(enabled: boolean): Promise<{
        success: boolean;
        enabled: boolean;
    }>;
    keyboardDown(key: string): Promise<{
        success: boolean;
        key: string;
    }>;
    keyboardUp(key: string): Promise<{
        success: boolean;
        key: string;
    }>;
    keyboardInsertText(text: string): Promise<{
        success: boolean;
        text: string;
    }>;
    mouseMove(x: number, y: number, steps?: number): Promise<{
        success: boolean;
        x: number;
        y: number;
    }>;
    mouseDown(options?: {
        button?: 'left' | 'right' | 'middle';
        clickCount?: number;
    }): Promise<{
        success: boolean;
    }>;
    mouseUp(options?: {
        button?: 'left' | 'right' | 'middle';
        clickCount?: number;
    }): Promise<{
        success: boolean;
    }>;
    mouseWheel(deltaX: number, deltaY: number): Promise<{
        success: boolean;
        deltaX: number;
        deltaY: number;
    }>;
    mouseClick(x: number, y: number, options?: {
        button?: 'left' | 'right' | 'middle';
        clickCount?: number;
        delay?: number;
    }): Promise<{
        success: boolean;
        x: number;
        y: number;
    }>;
    tap(selector: string): Promise<{
        success: boolean;
        selector: string;
    }>;
    touchscreenTap(x: number, y: number): Promise<{
        success: boolean;
        x: number;
        y: number;
    }>;
    setGeolocation(latitude: number, longitude: number, accuracy?: number): Promise<{
        success: boolean;
        latitude: number;
        longitude: number;
    }>;
    clearGeolocation(): Promise<{
        success: boolean;
        message: string;
    }>;
    getMetrics(): Promise<{
        success: boolean;
        metrics: {
            domContentLoaded: number;
            loadComplete: number;
            domInteractive: number;
            firstPaint: number;
            firstContentfulPaint: number;
        };
    }>;
    getCoverage(): Promise<{
        success: boolean;
        message: string;
    }>;
    stopCoverage(): Promise<{
        success: boolean;
        jsCoverage: number;
        cssCoverage: number;
    }>;
    getAccessibilitySnapshot(selector?: string): Promise<{
        success: boolean;
        snapshot: any;
    }>;
    installClock(time?: number | Date): Promise<{
        success: boolean;
        message: string;
    }>;
    setSystemTime(time: number | Date): Promise<{
        success: boolean;
        time: string;
    }>;
    fastForward(time: number): Promise<{
        success: boolean;
        time: number;
    }>;
    pauseClock(): Promise<{
        success: boolean;
        message: string;
    }>;
    resumeClock(): Promise<{
        success: boolean;
        message: string;
    }>;
    getByRole(role: string, options?: {
        name?: string;
    }): Promise<{
        success: boolean;
        count: number;
        role: string;
    }>;
    getByText(text: string | RegExp, options?: {
        exact?: boolean;
    }): Promise<{
        success: boolean;
        count: number;
        text: string;
    }>;
    getByLabel(text: string | RegExp, options?: {
        exact?: boolean;
    }): Promise<{
        success: boolean;
        count: number;
        label: string;
    }>;
    getByPlaceholder(text: string | RegExp, options?: {
        exact?: boolean;
    }): Promise<{
        success: boolean;
        count: number;
        placeholder: string;
    }>;
    getByTestId(testId: string): Promise<{
        success: boolean;
        count: number;
        testId: string;
    }>;
    getByAltText(text: string | RegExp, options?: {
        exact?: boolean;
    }): Promise<{
        success: boolean;
        count: number;
        altText: string;
    }>;
    getByTitle(text: string | RegExp, options?: {
        exact?: boolean;
    }): Promise<{
        success: boolean;
        count: number;
        title: string;
    }>;
    waitForFunction(fn: string, arg?: any, options?: {
        timeout?: number;
        polling?: number;
    }): Promise<{
        success: boolean;
    }>;
    waitForLoadState(state: 'load' | 'domcontentloaded' | 'networkidle', options?: {
        timeout?: number;
    }): Promise<{
        success: boolean;
        state: "load" | "domcontentloaded" | "networkidle";
    }>;
    storageState(path?: string): Promise<{
        success: boolean;
        state: {
            cookies: Array<{
                name: string;
                value: string;
                domain: string;
                path: string;
                expires: number;
                httpOnly: boolean;
                secure: boolean;
                sameSite: "Strict" | "Lax" | "None";
            }>;
            origins: Array<{
                origin: string;
                localStorage: Array<{
                    name: string;
                    value: string;
                }>;
            }>;
        };
    }>;
    restoreStorageState(state: any): Promise<{
        success: boolean;
        message: string;
    }>;
    grantPermissions(permissions: string[], options?: {
        origin?: string;
    }): Promise<{
        success: boolean;
        permissions: string[];
    }>;
    clearPermissions(): Promise<{
        success: boolean;
        message: string;
    }>;
    getBrowserVersion(): Promise<{
        success: boolean;
        version: string;
    }>;
    getBrowserContexts(): Promise<{
        success: boolean;
        count: number;
    }>;
    isConnected(): Promise<{
        success: boolean;
        connected: boolean;
    }>;
}
export default PlaywrightBrowserSkill;
