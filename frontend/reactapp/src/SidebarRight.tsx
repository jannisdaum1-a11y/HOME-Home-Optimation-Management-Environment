import {useState} from 'react';
import './SidebarRight.css';

type Asset = {
    image: string;
    [key: string]: unknown;
};

/**Define which keys should not be ediable or displayed */
const not_visible: string[] = ["class", "image"]

type SidebarRightProps = {
    selectedAsset:Asset | null;
    setAssets: React.Dispatch<React.SetStateAction<Asset[] | []>>;
    setSelectedAsset: React.Dispatch<React.SetStateAction<Asset | null>>;
}

type ParameterValue = string | number | boolean | null | undefined | Record<string, unknown>;

type ParameterGroupProps = {
    values: Record<string, unknown>;
    path: string[];
    updateValue: (path: string[], value: ParameterValue) => void;
};

function ParameterGroup({values, path, updateValue}: ParameterGroupProps) {
    return (
        <div className="ParameterGroup">
            {Object.entries(values).map(([name, value]) => {
                const valuePath = [...path, name];
                const isDictionary = value !== null && typeof value === 'object' && !Array.isArray(value);

                if (isDictionary) {
                    return (
                        <CollapsibleParameterGroup
                            key={valuePath.join('.')}
                            name={name}
                            values={value as Record<string, unknown>}
                            path={valuePath}
                            updateValue={updateValue}
                        />
                    );
                }

                return (
                    <div className="ParameterField" key={valuePath.join('.')}>
                        <label>{name}: </label>
                        <input
                            type={typeof value === 'boolean' ? 'checkbox' : typeof value === 'number' ? 'number' : 'text'}
                            {...(typeof value === 'boolean'
                                ? {checked: value}
                                : {value: String(value ?? '')})}
                            onChange={(event) => {
                                const nextValue = typeof value === 'boolean'
                                    ? event.currentTarget.checked
                                    : typeof value === 'number'
                                        ? Number(event.currentTarget.value)
                                        : event.currentTarget.value;
                                updateValue(valuePath, nextValue);
                            }}
                        />
                    </div>
                );
            })}
        </div>
    );
}

type CollapsibleParameterGroupProps = ParameterGroupProps & {
    name: string;
};

function CollapsibleParameterGroup({name, values, path, updateValue}: CollapsibleParameterGroupProps) {
    const [expanded, setExpanded] = useState(false);

    return (
        <div className="NestedParameterGroup">
            <button
                type="button"
                className="ParameterGroupToggle"
                onClick={() => setExpanded(current => !current)}
                aria-expanded={expanded}
            >
                <span aria-hidden="true">{expanded ? '▾' : '▸'}</span>
                {name}
            </button>
            {expanded && <ParameterGroup values={values} path={path} updateValue={updateValue} />}
        </div>
    );
}

function SidebarRight({selectedAsset, setAssets, setSelectedAsset} : SidebarRightProps){
    const asset = selectedAsset
    
    function updateValue(path: string[], value: ParameterValue) {
        if (!selectedAsset) {
            return;
        }

        const updateAsset = (asset: Asset) => {
            if (asset.name !== selectedAsset.name) {
                return asset;
            }

            const updatedAsset: Asset = {...asset};
            let target: Record<string, unknown> = updatedAsset;
            path.slice(0, -1).forEach(key => {
                const nestedValue = target[key];
                if (nestedValue && typeof nestedValue === 'object' && !Array.isArray(nestedValue)) {
                    const nestedCopy = {...nestedValue as Record<string, unknown>};
                    target[key] = nestedCopy;
                    target = nestedCopy;
                }
            });
            target[path[path.length - 1]] = value;
            return updatedAsset;
        };

        setAssets(prev => prev.map(updateAsset));
        setSelectedAsset(updateAsset(selectedAsset));
    }

    return (
    <div className='SideBarRight'>
    {
        asset === null && <p>Wählen Sie ein beliebiges Asset aus, um verfügbare Parameter zu variieren</p>
    }
    

    {asset && (
        <ParameterGroup
            values={Object.fromEntries(Object.entries(asset).filter(([name]) => !not_visible.includes(name)))}
            path={[]}
            updateValue={updateValue}
        />
    )}
</div>
);
}
export default SidebarRight;