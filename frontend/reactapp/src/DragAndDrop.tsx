import './DragAndDrop.css';
import assets from './assets/assets.json'

/** Initialize Counter for naming of objects */
const counter: Record<string,number> = {}
Object.keys(assets).forEach(element => {
    counter[element]=0;
});
type Asset = {
    image?: string;
    [key: string]: unknown;
};


function DisplayObject({object}: {object:Asset}) {
    return (
        <>
        <img src={object.image ?? ""} alt={String(object.name)}></img>
        <p>{String(object.name)}</p>
        </>
    )
}
type Dict = {
    [key: string]: unknown;
};
function isDictionary(value: unknown): value is Dict {
    return typeof value === 'object' && value !== null && !Array.isArray(value);
}

function findDefaultValue(defaults: Dict, key: string): unknown {
    if (key in defaults && !isDictionary(defaults[key])) {
        return defaults[key];
    }

    for (const value of Object.values(defaults)) {
        if (isDictionary(value)) {
            const defaultValue = findDefaultValue(value, key);
            if (defaultValue !== undefined) {
                return defaultValue;
            }
        }
    }

    return undefined;
}

function applyDefaults(dict: Dict, defaults: Dict): Dict {
    const result: Dict = {...dict};

    for (const [key, value] of Object.entries(result)) {
        if (isDictionary(value)) {
            result[key] = applyDefaults(value, defaults);
            continue;
        }

        const defaultValue = findDefaultValue(defaults, key);
        if ((value === null || value === undefined) && defaultValue !== undefined) {
            result[key] = structuredClone(defaultValue);
        }
    }

    return result;
}


type DragAndDropProps = {
    objects: Asset[];
    setObjects: React.Dispatch<React.SetStateAction<Asset[]>>;
    setSelectedObject: React.Dispatch<React.SetStateAction<Asset|null>>;
};
function DragAndDrop({objects, setObjects, setSelectedObject}: DragAndDropProps){

    function handleDropFromAsset(assetName: string | null) {
        if (!assetName || !(assetName in assets)) {
            return;
        }

        const object = assetName as keyof typeof assets;
        let data = structuredClone(assets[object]) as unknown as Asset;

        data = applyDefaults(data, objects[0] ?? {}) as Asset;

        data.name = data.name + "_" + counter[object]++;
        setObjects(prev => [...prev, data]);
        setSelectedObject(data);
    }

    function handleDrop(e: React.DragEvent<HTMLDivElement>) {
        e.preventDefault();
        const object = e.dataTransfer.getData("asset") || (window as Window & {__pendingAsset?: string}).__pendingAsset || null;
        handleDropFromAsset(object);
        delete (window as Window & {__pendingAsset?: string}).__pendingAsset;
    }

    function handleTouchDrop(e: React.TouchEvent<HTMLDivElement>) {
        const touch = e.changedTouches[0];
        if (!touch) {
            return;
        }

        const element = document.elementFromPoint(touch.clientX, touch.clientY);
        const object = (window as Window & {__pendingAsset?: string}).__pendingAsset || null;
        const deleteButton = element?.closest('.DeleteObject');
        const selectedObjectElement = element?.closest('.DisplayObject');

        if (deleteButton) {
            delete (window as Window & {__pendingAsset?: string}).__pendingAsset;
            return;
        }

        if (!object && selectedObjectElement) {
            const objectName = selectedObjectElement.getAttribute('data-object-name');
            const nextObject = objectName ? objects.find(item => item.name === objectName) ?? null : null;
            if (nextObject) {
                setSelectedObject(nextObject);
            }
            delete (window as Window & {__pendingAsset?: string}).__pendingAsset;
            return;
        }

        const isEmptyBackgroundTap = !element || !element.closest('.DisplayObject') && !element.closest('.DeleteObject');

        if (isEmptyBackgroundTap && !object) {
            setSelectedObject(objects[0] ?? null);
            delete (window as Window & {__pendingAsset?: string}).__pendingAsset;
            return;
        }

        if (!element || !element.closest('.DragAndDrop')) {
            delete (window as Window & {__pendingAsset?: string}).__pendingAsset;
            return;
        }

        e.preventDefault();
        handleDropFromAsset(object);
        delete (window as Window & {__pendingAsset?: string}).__pendingAsset;
    }

    function handleDelete(objectName: unknown) {
        setObjects(prev => prev.filter(object => object.name !== objectName));
        setSelectedObject(prev => prev && prev.name === objectName ? null : prev);
    }


    return (
        <div className='DragAndDrop' 
        onDragOver={(e) => e.preventDefault()}
        onDrop={handleDrop}
        onClick={(event) => {
            const target = event.target as HTMLElement;
            if (!target.closest('.DisplayObject') && !target.closest('.DeleteObject')) {
                setSelectedObject(objects[0] ?? null);
            }
        }}
        onTouchEnd={handleTouchDrop}>
            {
                objects.length===0 && (<p>Ziehen Sie die gewünschten Elemente in den unteren Bereich</p>)
            }
            {
                objects.map((element) => (
                    !(element.name==="config") &&
                    <div className='DisplayObject'
                     key={String(element.name)}
                     data-object-name={String(element.name)}
                     onClick={() => setSelectedObject(element)}>
                        <DisplayObject object={element}></DisplayObject>
                        <button
                            type='button'
                            className='DeleteObject'
                            aria-label={`${String(element.name)} löschen`}
                            onClick={(e) => {
                                e.stopPropagation();
                                handleDelete(element.name);
                            }}
                        >
                            Löschen
                        </button>
                    </div>
                )
            )
            }
        </div>
    );
}

export default DragAndDrop